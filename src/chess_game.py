"""
Main entry point to play a game
"""
import argparse
from chess_core import ChessGame
from chess_alt_rules import ChessGameAlt
from chess_periodic import ChessGamePeriodic

def main():
    """Choose and start a chess game
    """
    parser = argparse.ArgumentParser(description='Play a chess game')
    parser.add_argument(
        '--anything-goes',
        action='store_true',
        help="Modify rules... so that there aren't any"
    )
    parser.add_argument(
        '--periodic',
        action='store_true',
        help="Play on a board with periodic boundary conditions (torus topology)"
    )
    args = parser.parse_args()
    if args.periodic:
        ChessGamePeriodic()
        return
    if args.anything_goes:
        ChessGameAlt()
        return
    # else
    ChessGame()

if __name__ == '__main__':
    main()
