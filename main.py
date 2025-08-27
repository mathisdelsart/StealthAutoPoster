import logging
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Union

sys.path.append(str(Path(__file__).parent) + '/facebook_automation')

from facebook_automation import FacebookAutomation

GroupType = Union[str, Tuple[str, str]]


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('facebook_automation.log', mode='a')
        ]
    )


def load_groups_from_file(file_path: str) -> List[GroupType]:
    """
    Load groups from a text file.
    Supports lines with just URL or 'name | url'.
    """
    groups: List[GroupType] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    parts = [p.strip() for p in line.split('|', 1)]
                    if len(parts) == 2:
                        groups.append((parts[0], parts[1]))
                        continue
                groups.append(line)
        return groups
    except FileNotFoundError:
        logging.error(f"Groups file not found: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error reading groups file: {e}")
        return []


def save_groups_to_file(groups: List[GroupType], file_path: str) -> bool:
    """Save extracted groups to a text file (always 'name | url' if name available)"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for group in groups:
                if isinstance(group, tuple):
                    name, url = group
                    line = f"{name} | {url}"
                else:
                    line = group
                f.write(line + "\n")
        return True
    except Exception as e:
        logging.error(f"Error saving groups to file {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Facebook Group Automation Tool')
    
    parser.add_argument('--mode', choices=['full', 'login', 'extract', 'publish'], 
                        default='full', help='Automation mode to run')
    parser.add_argument('--dry-run', action='store_false', help='Run in test mode without actually posting')
    parser.add_argument('--max-groups', type=int, help='Maximum number of groups to process')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Logging level')
    parser.add_argument('--output-file', type=str, default='groups.txt', help='Output file for extracted groups')
    parser.add_argument('--groups-file', type=str, help='File containing group URLs (publish mode)')
    parser.add_argument('--post-content', type=str, help='Custom post content (publish mode)')
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    automation = FacebookAutomation()
    driver = automation.start()

    # Store extracted groups for later use
    groups = None
    
    if args.dry_run:
        automation.update_config(dry_run=True)
    if args.max_groups:
        automation.update_config(max_groups=args.max_groups)
    
    try:
        success = automation.login()

        if not success:
            logger.error("Login failed")
            sys.exit(1)
        
        logger.info("Login successful")
        
        if args.mode == 'extract' or args.mode == 'full':
            groups = automation.extract_groups()
            logger.info(f"Extracted {len(groups)} groups")
            
            if groups:
                save_success = save_groups_to_file(groups, args.output_file)
                if save_success:
                    logger.info(f"Groups saved to {args.output_file}")
                else:
                    logger.error(f"Failed to save groups to {args.output_file}")
                    sys.exit(1)
                
                for i, group in enumerate(groups, 1):
                    if isinstance(group, tuple):
                        name, url = group
                        print(f"{i:3d}. {name}")
                        print(f"     {url}")
                    else:
                        print(f"{i:3d}. {group}")
            else:
                logger.warning("No groups were extracted")
                sys.exit(1)
        
        if args.mode == 'publish' or args.mode == 'full':
            if args.mode == 'publish' and not args.groups_file:
                logger.error("--groups-file is required for publish mode")
                sys.exit(1)
            
            if groups is None:
                groups = load_groups_from_file(args.groups_file)

            if groups == []:
                logger.error(f"No groups found in {args.groups_file}")
                sys.exit(1)
            
            stats = automation.publish_to_specific_groups(groups, post_content=args.post_content)
            print(automation.get_stats_summary(stats))

    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        print("\nAutomation stopped by user")
    
    except Exception as e:
        logger.error(f"Automation failed with error: {e}")
        print(f"\n❌ Automation failed: {e}")
        sys.exit(1)
    
    finally:
        automation.stop()

if __name__ == "__main__":
    main()
