import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "checkers.py"
SPEC = importlib.util.spec_from_file_location("checkers", MODULE_PATH)
checkers = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checkers)


class CheckersTests(unittest.TestCase):
    def test_initial_board_has_twenty_four_pieces(self):
        board = checkers.PlateauDames()
        pieces = sum(
            board.obtenir_piece(checkers.Position(row, col)) != checkers.PieceType.EMPTY
            for row in range(8)
            for col in range(8)
        )
        self.assertEqual(pieces, 24)

    def test_capture_is_mandatory(self):
        board = checkers.PlateauDames()
        board.plateau = [[checkers.PieceType.EMPTY for _ in range(8)] for _ in range(8)]
        board.placer_piece(checkers.Position(5, 0), checkers.PieceType.PION_BLANC)
        board.placer_piece(checkers.Position(4, 1), checkers.PieceType.PION_NOIR)
        moves = checkers.MoteurLogique(board).tous_mouvements_valides(checkers.Joueur.BLANC)
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].fin, checkers.Position(3, 2))
        self.assertEqual(moves[0].captures, [checkers.Position(4, 1)])

    def test_promotion(self):
        board = checkers.PlateauDames()
        board.plateau = [[checkers.PieceType.EMPTY for _ in range(8)] for _ in range(8)]
        start = checkers.Position(1, 2)
        end = checkers.Position(0, 1)
        board.placer_piece(start, checkers.PieceType.PION_BLANC)
        self.assertTrue(checkers.MoteurLogique(board).executer_mouvement(checkers.Mouvement(start, end), checkers.Joueur.BLANC))
        self.assertEqual(board.obtenir_piece(end), checkers.PieceType.DAME_BLANCHE)

    def test_minimax_returns_a_legal_move(self):
        board = checkers.PlateauDames()
        legal = checkers.MoteurLogique(board).tous_mouvements_valides(checkers.Joueur.NOIR)
        _, move = checkers.MiniMax(profondeur_max=2).minimax(board, 2, True, checkers.Joueur.NOIR)
        self.assertIn(move, legal)


if __name__ == "__main__":
    unittest.main()
