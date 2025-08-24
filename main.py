"""
Main execution script for Facebook automation
"""
import logging
import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent) + '/facebook_automation')

from facebook_automation import FacebookAutomation
from config import Config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('facebook_automation.log', mode='a')
        ]
    )


def main():
    """Main execution function with command line interface"""
    parser = argparse.ArgumentParser(description='Facebook Group Automation Tool')
    
    # Action arguments
    parser.add_argument('--mode', choices=['full', 'login-test', 'extract-only', 'publish-only'], 
                       default='full', help='Automation mode to run')
    
    # Configuration overrides
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in test mode without actually posting')
    parser.add_argument('--max-groups', type=int, 
                       help='Maximum number of groups to process')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    # Extract-only options
    parser.add_argument('--include-names', action='store_true', 
                       help='Include group names when extracting (extract-only mode)')
    parser.add_argument('--output-file', type=str, default='groups.txt',
                       help='Output file for extracted groups (extract-only mode, default: groups.txt)')
    
    # Publish-only options
    parser.add_argument('--groups-file', type=str, 
                       help='File containing group URLs (publish-only mode)')
    parser.add_argument('--post-content', type=str, 
                       help='Custom post content (publish-only mode)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize automation
        automation = FacebookAutomation()
        
        # Apply command line overrides
        if args.dry_run:
            automation.update_config(dry_run=True)
        if args.max_groups:
            automation.update_config(max_groups=args.max_groups)
        
        # Execute based on mode
        if args.mode == 'full':
            stats = automation.run_full_automation()
            print(automation.get_stats_summary(stats))
            
        elif args.mode == 'login-test':
            success = automation.login_only()
            print(f"✅ Login test {'passed' if success else 'failed'}")
            
        elif args.mode == 'extract-only':
            groups = automation.extract_groups_only(include_names=args.include_names)
            print(f"\n📋 Extracted {len(groups)} groups:")

            if groups:
                # Save groups to file
                save_success = save_groups_to_file(groups, args.output_file, args.include_names)
                
                if save_success:
                    print(f"\n📋 Extracted {len(groups)} groups and saved to '{args.output_file}'")
                    logger.info(f"Groups successfully saved to {args.output_file}")
                else:
                    print(f"\n📋 Extracted {len(groups)} groups but failed to save to file")
                    logger.error(f"Failed to save groups to {args.output_file}")
                
                # Also display groups in console
                print(f"\n📋 Groups list:")
                for i, group in enumerate(groups, 1):
                    if isinstance(group, tuple):
                        name, url = group
                        print(f"{i:3d}. {name}")
                        print(f"     {url}")
                    else:
                        print(f"{i:3d}. {group}")
            else:
                print("\n!! No groups extracted !!")
                logger.warning("No groups were extracted")
            
        elif args.mode == 'publish-only':
            if not args.groups_file:
                logger.error("--groups-file is required for publish-only mode")
                sys.exit(1)
            
            # Load groups from file
            groups = load_groups_from_file(args.groups_file)
            if not groups:
                logger.error(f"No groups found in {args.groups_file}")
                sys.exit(1)
            
            stats = automation.publish_to_specific_groups(
                groups, post_content=args.post_content
            )
            print(automation.get_stats_summary(stats))
            
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        print("\n!! Automation stopped by user !!")
        
    except Exception as e:
        logger.error(f"Automation failed with error: {e}")
        print(f"\n❌ Automation failed: {e}")
        sys.exit(1)


def load_groups_from_file(file_path: str) -> list:
    """
    Load groups from a text file
    
    Args:
        file_path: Path to file containing group URLs (one per line)
        
    Returns:
        list: List of group URLs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            groups = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        return groups
    except FileNotFoundError:
        logging.error(f"Groups file not found: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error reading groups file: {e}")
        return []


def save_groups_to_file(groups: list, file_path: str, include_names: bool = False) -> bool:
    """
    Save extracted groups to a text file
    
    Args:
        groups: List of groups (URLs or tuples of (name, url))
        file_path: Path to output file
        include_names: Whether groups include names
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for group in groups:
                if isinstance(group, tuple) and include_names:
                    # If it's a tuple (name, url), write only the URL
                    name, url = group
                    f.write(f"{url}\n")
                else:
                    # If it's just a URL string
                    f.write(f"{group}\n")
        
        return True
        
    except Exception as e:
        logging.error(f"Error saving groups to file {file_path}: {e}")
        return False


if __name__ == "__main__":    
    main()
