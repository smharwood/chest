"""
Main entry point to play a game
"""
import argparse
from chess_core import ChessGame
from chess_alt_rules import ChessGameAlt

def main():
    """Choose and start a chess game
    """
    parser = argparse.ArgumentParser(description='Play a chess game')
    parser.add_argument(
        '--anything-goes',
        action='store_true',
        help="Modify rules... so that there aren't any"
    )
    args = parser.parse_args()
    if args.anything_goes:
        ChessGameAlt()
        return
    # else
    ChessGame()

if __name__ == '__main__':
    main()
