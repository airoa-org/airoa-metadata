#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple utility for converting AIROA metadata between versions.
Only supports ascending version conversion (e.g., v1.1 -> v1.3).

Usage:
    python convert_metadata.py input.json --target-version 1.3 --output output.json
    python convert_metadata.py input.json --target-version 1.2 --in-place
    python convert_metadata.py input.json --target-version 1.3  # outputs to stdout
"""

import argparse
import dataclasses
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from airoa_metadata import (
    MetadataV0_0, MetadataV1_0, MetadataV1_1, MetadataV1_2, MetadataV1_3,
    MetadataLoader
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# External git repo mapping for components
GIT_REPO_MAPPING = {
    "data_collection": "https://github.com/airoa-org/hsr_data_collection.git",
    "data_capture": "https://github.com/airoa-org/hsr_data_collection.git", 
    "interface": "https://github.com/airoa-org/hsr_leader_teleop.git"
}


def add_git_uris(data):
    """Add git URIs to components based on their role."""
    if "context" in data and "components" in data["context"]:
        for component in data["context"]["components"]:
            if "source" in component and "git" in component["source"]:
                git_info = component["source"]["git"]
                role = component.get("role", "")
                
                # Add URI if not present or empty
                if not git_info.get("uri"):
                    git_info["uri"] = GIT_REPO_MAPPING.get(role, "")
    
    return data


def add_data_collection_component(data):
    """Add data_collection component if git_branch and git_hash are present."""
    if ("git_branch" in data and "git_hash" in data and 
        data["git_branch"] and data["git_hash"]):
        
        if "context" not in data:
            data["context"] = {}
        if "components" not in data["context"]:
            data["context"]["components"] = []
        
        # Check if data_collection component already exists
        existing_roles = [comp.get("role") for comp in data["context"]["components"]]
        if "data_collection" not in existing_roles:
            data_collection_component = {
                "role": "data_collection",
                "name": "rosbag_manager", 
                "source": {
                    "git": {
                        "uri": GIT_REPO_MAPPING.get("data_collection", ""),
                        "hash": data["git_hash"],
                        "branch": data["git_branch"],
                        "tag": None
                    }
                }
            }
            data["context"]["components"].append(data_collection_component)
    
    return data


def remove_null_values(obj):
    """Recursively remove null values from dictionaries and lists."""
    if isinstance(obj, dict):
        return {k: remove_null_values(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_null_values(item) for item in obj if item is not None]
    else:
        return obj


def get_version_class(version: str):
    """Get the metadata class for a given version string."""
    version_map = {
        "0.0": MetadataV0_0,
        "1.0": MetadataV1_0,
        "1.1": MetadataV1_1,
        "1.2": MetadataV1_2,
        "1.3": MetadataV1_3,
    }
    
    if version not in version_map:
        available = ", ".join(version_map.keys())
        raise ValueError(f"Unsupported version '{version}'. Available versions: {available}")
    
    return version_map[version]


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
    def parse_version(v):
        return tuple(map(int, v.split('.')))
    
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)
    
    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 > parsed_v2:
        return 1
    else:
        return 0


def convert_metadata(input_file: Path, target_version: str, output_file: Path = None):
    """
    Convert metadata file to target version.
    
    Args:
        input_file: Path to input JSON file
        target_version: Target version string (e.g., "1.3")
        output_file: Path to output file (if None, outputs to stdout)
    
    Returns:
        Dict containing the converted metadata
    """
    # Load the input file
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Get current version from the data
    current_version = data.get("version")
    if not current_version:
        logger.error("Input file does not contain a 'version' field")
        sys.exit(1)
    
    # Check if conversion is needed
    if current_version == target_version:
        logger.info(f"Input file is already version {target_version}, no conversion needed")
        if output_file:
            # Still copy to output file if specified
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"File copied to {output_file}")
        else:
            # Output to stdout
            json.dump(data, sys.stdout, indent=2)
        return data
    
    # Check if this is an ascending conversion
    if compare_versions(current_version, target_version) > 0:
        logger.error(f"Descending conversion from {current_version} to {target_version} is not supported")
        sys.exit(1)
    
    # Apply git repo mapping and add data collection component if needed
    data = add_data_collection_component(data)
    data = add_git_uris(data)
    
    # Load metadata using the loader (which auto-detects version)
    try:
        loader = MetadataLoader()
        metadata = loader.load_from_dict(data)
        logger.info(f"Loaded metadata version {metadata.version}")
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        sys.exit(1)
    
    # Convert to target version
    try:
        target_class = get_version_class(target_version)
        converted = target_class.convert(metadata)
        logger.info(f"Converted from version {current_version} to {target_version}")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        sys.exit(1)
    
    # Convert back to dict for output and apply post-processing
    converted_dict = dataclasses.asdict(converted)
    converted_dict = add_git_uris(converted_dict)
    
    # Add $schema field for v1.3
    if target_version == "1.3":
        converted_dict["$schema"] = "https://raw.githubusercontent.com/airoa-org/airoa-metadata/refs/tags/v1.3/airoa_metadata/schemas/v1_3.json"
    
    converted_dict = remove_null_values(converted_dict)
    
    # Write output
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(converted_dict, f, indent=2)
            logger.info(f"Converted metadata saved to {output_file}")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        # Output to stdout
        json.dump(converted_dict, sys.stdout, indent=2)
    
    return converted_dict


def main():
    parser = argparse.ArgumentParser(
        description="Convert AIROA metadata between versions (ascending only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to v1.3 and save to new file
  python convert_metadata.py input.json --target-version 1.3 --output output.json
  
  # Convert in-place to v1.2
  python convert_metadata.py metadata.json --target-version 1.2 --in-place
  
  # Convert and output to stdout
  python convert_metadata.py input.json --target-version 1.3

Supported versions: 0.0, 1.0, 1.1, 1.2, 1.3
        """
    )
    
    parser.add_argument("input", help="Input metadata JSON file", type=Path)
    parser.add_argument("--target-version", "-t", required=True, 
                       help="Target version (e.g., 1.3)")
    parser.add_argument("--in-place", "-i", action="store_true",
                       help="Modify the input file in-place")
    parser.add_argument("--output", "-o", type=Path,
                       help="Output file path (if not specified, outputs to stdout)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.input.exists():
        logger.error(f"Input file '{args.input}' does not exist")
        sys.exit(1)
    
    # Determine output file
    output_file = None
    if args.in_place:
        if args.output:
            logger.error("Cannot use --in-place with --output option")
            sys.exit(1)
        output_file = args.input
    elif args.output:
        output_file = args.output
    # If neither --in-place nor --output specified, output goes to stdout
    
    # Perform conversion
    try:
        convert_metadata(args.input, args.target_version, output_file)
    except KeyboardInterrupt:
        logger.error("Conversion cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()