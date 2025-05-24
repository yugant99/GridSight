import pandas as pd
import os
import json
import xml.etree.ElementTree as ET

def analyze_xml_file(file_path):
    """Analyzes a single XML file to generate its schema."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        file_name = os.path.basename(file_path)

        schema = {
            "fileName": file_name,
            "type": "XML",
            "rootElement": root.tag,
            "elements_attributes": {}, # Store unique elements and their attributes
            "potentialKeys": []
        }
        
        unique_elements_attributes = {}
        potential_keys_xml_set = set()
        key_patterns = ['id', 'key', 'guid', 'identifier', 'uuid']

        for elem in root.iter(): # Iterate through all elements in the document
            # Store attributes for each tag
            if elem.tag not in unique_elements_attributes:
                unique_elements_attributes[elem.tag] = set(elem.attrib.keys())
            else:
                unique_elements_attributes[elem.tag].update(elem.attrib.keys())
            
            # Potential key detection from attributes
            for attr_name in elem.attrib.keys():
                if any(pk_pattern in attr_name.lower() for pk_pattern in key_patterns):
                    potential_keys_xml_set.add(f"{elem.tag}@{attr_name}")
            
            # Potential key detection from element tag itself (if it implies an ID)
            if any(pk_pattern in elem.tag.lower() for pk_pattern in key_patterns):
                 potential_keys_xml_set.add(elem.tag)

        schema["elements_attributes"] = {tag: sorted(list(attrs)) for tag, attrs in unique_elements_attributes.items()}
        schema["potentialKeys"] = sorted(list(potential_keys_xml_set))
        
        return schema
    except ET.ParseError as e:
        print(f"Error parsing XML file {file_path}: {e}")
        return {
            "fileName": os.path.basename(file_path),
            "type": "XML",
            "error": f"ParseError: {e}"
        }
    except Exception as e:
        print(f"Error processing XML file {file_path}: {e}")
        return {
            "fileName": os.path.basename(file_path),
            "type": "XML",
            "error": f"GeneralError: {e}"
        }

def analyze_files(directory='.'):
    all_files = os.listdir(directory)
    csv_files = sorted([f for f in all_files if f.endswith('.csv')])
    xml_files = sorted([f for f in all_files if f.endswith('.xml')])

    schemas = []
    csv_dataframes = {} # Stores successfully loaded DataFrames {filename: df}
    xml_structures = {} # Stores successfully parsed XML info {filename: {"elements": [], "attributes": []}}

    potential_keys_patterns_csv = ['id', '_id', 'key', '_key', 'name', 'code', 'identifier', 'uuid']

    print(f"Found {len(csv_files)} CSV files: {csv_files}")
    print(f"Found {len(xml_files)} XML files: {xml_files}")

    # Process CSV files
    for csv_file in csv_files:
        file_path = os.path.join(directory, csv_file)
        df = None
        try:
            try:
                df = pd.read_csv(file_path, low_memory=False)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, low_memory=False, encoding='latin1')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, low_memory=False, encoding='iso-8859-1')
            
            csv_dataframes[csv_file] = df
            file_schema = {
                "fileName": csv_file,
                "type": "CSV",
                "columns": []
            }
            if df.empty:
                file_schema["columns"] = "File is empty or could not be parsed correctly."
                schemas.append(file_schema)
                print(f"Warning: CSV file {csv_file} is empty or unreadable.")
                continue

            null_counts = df.isnull().sum()
            for col in df.columns:
                # Check if column exists in null_counts (it should, but defensive check)
                is_nullable = int(null_counts[col]) > 0 if col in null_counts else True 
                
                # Uniqueness check (can be slow for large columns, consider sampling or skipping if performance is an issue)
                try:
                    is_unique = df[col].is_unique if not df[col].empty else True # Treat empty column as unique
                except Exception: # Handle potential errors with complex data types in is_unique
                    is_unique = False 

                col_info = {
                    "name": str(col), # Ensure column name is string
                    "dataType": str(df[col].dtype),
                    "nullable": is_nullable,
                    "isUnique": is_unique,
                    "potentialKey": any(pattern in str(col).lower() for pattern in potential_keys_patterns_csv)
                }
                file_schema["columns"].append(col_info)
            schemas.append(file_schema)
            print(f"Analyzed schema for CSV: {csv_file}")
        except Exception as e:
            schemas.append({"fileName": csv_file, "type": "CSV", "error": str(e)})
            print(f"Error reading or processing CSV {csv_file}: {e}")
            if csv_file in csv_dataframes: # Remove if it was added but failed later
                del csv_dataframes[csv_file]
            continue

    # Process XML files
    for xml_file in xml_files:
        file_path = os.path.join(directory, xml_file)
        xml_schema_info = analyze_xml_file(file_path)
        schemas.append(xml_schema_info)
        if "error" not in xml_schema_info:
            xml_structures[xml_file] = {
                "elements": list(xml_schema_info.get("elements_attributes", {}).keys()),
                "attributes": sorted(list(set(attr for tag_attrs in xml_schema_info.get("elements_attributes", {}).values() for attr in tag_attrs)))
            }
            print(f"Analyzed schema for XML: {xml_file}")
        else:
            print(f"Skipped schema analysis for XML due to error: {xml_file}")


    # Identify relationships
    relationships = []
    
    # 1. CSV to CSV relationships
    csv_file_names = list(csv_dataframes.keys())
    for i in range(len(csv_file_names)):
        for j in range(i + 1, len(csv_file_names)):
            file1_name = csv_file_names[i]
            file2_name = csv_file_names[j]
            # Ensure dataframes were loaded successfully
            if file1_name not in csv_dataframes or file2_name not in csv_dataframes:
                continue
            df1 = csv_dataframes[file1_name]
            df2 = csv_dataframes[file2_name]
            
            if df1.empty or df2.empty: # Skip if one of the dataframes is empty
                continue

            common_columns = list(set(str(c) for c in df1.columns) & set(str(c) for c in df2.columns)) # Ensure column names are strings
            if common_columns:
                relationships.append({
                    "type": "CSV-CSV",
                    "file1": file1_name,
                    "file2": file2_name,
                    "linkingColumns": common_columns,
                    "details": "Common column names found."
                })

    # 2. XML to XML relationships
    xml_file_names_processed = list(xml_structures.keys())
    for i in range(len(xml_file_names_processed)):
        for j in range(i + 1, len(xml_file_names_processed)):
            file1_name = xml_file_names_processed[i]
            file2_name = xml_file_names_processed[j]
            struct1 = xml_structures[file1_name]
            struct2 = xml_structures[file2_name]

            common_elements = list(set(struct1.get("elements", [])) & set(struct2.get("elements", [])))
            common_attributes = list(set(struct1.get("attributes", [])) & set(struct2.get("attributes", [])))
            
            link_features = {}
            relationship_details_parts = []
            if common_elements:
                link_features["elements"] = common_elements
                relationship_details_parts.append(f"Common elements: {common_elements}")
            if common_attributes:
                link_features["attributes"] = common_attributes
                relationship_details_parts.append(f"Common attributes: {common_attributes}")

            if link_features: # Only add if there are common elements or attributes
                relationships.append({
                    "type": "XML-XML",
                    "file1": file1_name,
                    "file2": file2_name,
                    "linkingFeatures": link_features,
                    "details": "; ".join(relationship_details_parts) if relationship_details_parts else "Potential link based on structure."
                })

    # 3. CSV to XML relationships
    for csv_file_name, df in csv_dataframes.items():
        if df.empty:
            continue
        csv_cols_lower = {str(col).lower() for col in df.columns} # Use lower case for matching

        for xml_file_name, xml_struct in xml_structures.items():
            xml_elements_lower = {el.lower() for el in xml_struct.get("elements", [])}
            xml_attributes_lower = {attr.lower() for attr in xml_struct.get("attributes", [])}
            
            matching_csv_xml_elements = [col for col in df.columns if str(col).lower() in xml_elements_lower]
            matching_csv_xml_attributes = [col for col in df.columns if str(col).lower() in xml_attributes_lower]

            common_fields_details = []
            if matching_csv_xml_elements:
                common_fields_details.append(f"CSV columns matching XML elements: {matching_csv_xml_elements}")
            if matching_csv_xml_attributes:
                common_fields_details.append(f"CSV columns matching XML attributes: {matching_csv_xml_attributes}")
            
            if common_fields_details:
                relationships.append({
                    "type": "CSV-XML",
                    "csvFile": csv_file_name,
                    "xmlFile": xml_file_name,
                    "matchingFieldDetails": common_fields_details,
                    "details": "CSV column names (case-insensitive) match XML element tags or attribute names."
                })
    
    result = {
        "schemas": schemas,
        "potentialRelationships": relationships
    }
    return result

if __name__ == "__main__":
    analysis_result = analyze_files()
    print("\n--- File Analysis Report (JSON) ---")
    print(json.dumps(analysis_result, indent=2, ensure_ascii=False))

    # Optional Markdown output
    # print("\n\n--- File Analysis Report (Markdown) ---")
    # print("## File Schemas")
    # for schema in analysis_result.get("schemas", []):
    #     print(f"### {schema.get('fileName', 'N/A')} ({schema.get('type', 'N/A')})")
    #     if "error" in schema:
    #         print(f"- **Error**: {schema['error']}")
    #     elif schema.get('type') == 'CSV':
    #         if isinstance(schema.get('columns'), str): # Handles empty/unreadable CSV message
    #              print(f"- {schema.get('columns')}")
    #         else:
    #             print("| Column Name | Data Type | Nullable | Unique | Potential Key |")
    #             print("|-------------|-----------|----------|--------|---------------|")
    #             for col in schema.get('columns', []):
    #                 print(f"| {col.get('name','N/A')} | {col.get('dataType','N/A')} | {col.get('nullable','N/A')} | {col.get('isUnique','N/A')} | {col.get('potentialKey','N/A')} |")
    #     elif schema.get('type') == 'XML':
    #         print(f"- Root Element: `{schema.get('rootElement', 'N/A')}`")
    #         print("- Elements and their Attributes:")
    #         for elem, attrs in schema.get("elements_attributes", {}).items():
    #             attr_str = ', '.join(f"`{a}`" for a in attrs) if attrs else 'None'
    #             print(f"  - `{elem}`: Attributes - {attr_str}")
    #         pk_str = ', '.join(f"`{k}`" for k in schema.get('potentialKeys', [])) if schema.get('potentialKeys') else 'None'
    #         print(f"- Potential Keys (elements/attributes): {pk_str}")
    #     print("\n")

    # print("## Potential Relationships")
    # if analysis_result.get("potentialRelationships"):
    #     for rel in analysis_result.get("potentialRelationships", []):
    #         if rel.get('type') == 'CSV-CSV':
    #             print(f"- **{rel.get('type')}:** `{rel.get('file1','N/A')}` <-> `{rel.get('file2','N/A')}`")
    #             print(f"  - Linking Columns: `{', '.join(rel.get('linkingColumns',[]))}`")
    #         elif rel.get('type') == 'XML-XML':
    #             print(f"- **{rel.get('type')}:** `{rel.get('file1','N/A')}` <-> `{rel.get('file2','N/A')}`")
    #             features = rel.get('linkingFeatures',{})
    #             if features.get("elements"):
    #                 print(f"  - Common Elements: `{', '.join(features.get('elements',[]))}`")
    #             if features.get("attributes"):
    #                 print(f"  - Common Attributes: `{', '.join(features.get('attributes',[]))}`")
    #         elif rel.get('type') == 'CSV-XML':
    #             print(f"- **{rel.get('type')}:** `{rel.get('csvFile','N/A')}` (CSV) <-> `{rel.get('xmlFile','N/A')}` (XML)")
    #             for detail in rel.get('matchingFieldDetails',[]):
    # медицинский робот       print(f"  - {detail}")
    #         print(f"  - Details: {rel.get('details','N/A')}")
    #         print("\n")
    # else:
    #     print("No potential relationships detected based on current heuristics.") 