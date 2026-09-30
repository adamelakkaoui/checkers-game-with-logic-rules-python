import copy
import math
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum


class PieceType(Enum):
    EMPTY = 0
    PION_BLANC = 1
    PION_NOIR = 2
    DAME_BLANCHE = 3
    DAME_NOIRE = 4


class Joueur(Enum):
    BLANC = 1
    NOIR = 2


@dataclass
class Position:
    ligne: int
    colonne: int

    def __eq__(self, other):
        return self.ligne == other.ligne and self.colonne == other.colonne

    def __hash__(self):
        return hash((self.ligne, self.colonne))


@dataclass
class Mouvement:
    debut: Position
    fin: Position
    captures: List[Position] = None

    def __post_init__(self):
        if self.captures is None:
            self.captures = []


class ReglesDames:
    """Classe contenant toutes les règles logiques du jeu de dames"""

    @staticmethod
    def est_position_valide(pos: Position, taille_plateau: int = 8) -> bool:
        """Règle logique: Une position est valide si elle est dans les limites du plateau"""
        return 0 <= pos.ligne < taille_plateau and 0 <= pos.colonne < taille_plateau

    @staticmethod
    def est_case_jouable(pos: Position) -> bool:
        """Règle logique: Seules les cases noires sont jouables (somme ligne+colonne impaire)"""
        return (pos.ligne + pos.colonne) % 2 == 1

    @staticmethod
    def appartient_au_joueur(piece: PieceType, joueur: Joueur) -> bool:
        """Règle logique: Détermine si une pièce appartient au joueur"""
        if joueur == Joueur.BLANC:
            return piece in [PieceType.PION_BLANC, PieceType.DAME_BLANCHE]
        else:
            return piece in [PieceType.PION_NOIR, PieceType.DAME_NOIRE]

    @staticmethod
    def est_adversaire(piece: PieceType, joueur: Joueur) -> bool:
        """Règle logique: Détermine si une pièce appartient à l'adversaire"""
        if joueur == Joueur.BLANC:
            return piece in [PieceType.PION_NOIR, PieceType.DAME_NOIRE]
        else:
            return piece in [PieceType.PION_BLANC, PieceType.DAME_BLANCHE]

    @staticmethod
    def est_dame(piece: PieceType) -> bool:
        """Règle logique: Détermine si une pièce est une dame"""
        return piece in [PieceType.DAME_BLANCHE, PieceType.DAME_NOIRE]

    @staticmethod
    def doit_devenir_dame(pos: Position, piece: PieceType) -> bool:
        """Règle logique: Un pion devient dame quand il atteint la ligne opposée"""
        if piece == PieceType.PION_BLANC and pos.ligne == 0:
            return True
        elif piece == PieceType.PION_NOIR and pos.ligne == 7:
            return True
        return False

    @staticmethod
    def directions_mouvement_pion(joueur: Joueur) -> List[Tuple[int, int]]:
        """Règle logique: Directions de mouvement pour les pions"""
        if joueur == Joueur.BLANC:
            return [(-1, -1), (-1, 1)]  # Vers le haut
        else:
            return [(1, -1), (1, 1)]  # Vers le bas

    @staticmethod
    def directions_mouvement_dame() -> List[Tuple[int, int]]:
        """Règle logique: Directions de mouvement pour les dames"""
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]


class PlateauDames:
    """Représentation du plateau de jeu avec logique pure"""

    def __init__(self, taille: int = 8):
        self.taille = taille
        self.plateau = self._initialiser_plateau()

    def _initialiser_plateau(self) -> List[List[PieceType]]:
        """Initialise le plateau selon les règles standard des dames"""
        plateau = [[PieceType.EMPTY for _ in range(self.taille)] for _ in range(self.taille)]

        # Placement des pions noirs (3 premières lignes, cases noires)
        for ligne in range(3):
            for col in range(self.taille):
                if ReglesDames.est_case_jouable(Position(ligne, col)):
                    plateau[ligne][col] = PieceType.PION_NOIR

        # Placement des pions blancs (3 dernières lignes, cases noires)
        for ligne in range(5, 8):
            for col in range(self.taille):
                if ReglesDames.est_case_jouable(Position(ligne, col)):
                    plateau[ligne][col] = PieceType.PION_BLANC

        return plateau

    def obtenir_piece(self, pos: Position) -> PieceType:
        """Obtient la pièce à une position donnée"""
        if ReglesDames.est_position_valide(pos, self.taille):
            return self.plateau[pos.ligne][pos.colonne]
        return PieceType.EMPTY

    def placer_piece(self, pos: Position, piece: PieceType):
        """Place une pièce à une position donnée"""
        if ReglesDames.est_position_valide(pos, self.taille):
            self.plateau[pos.ligne][pos.colonne] = piece

    def obtenir_positions_joueur(self, joueur: Joueur) -> List[Position]:
        """Obtient toutes les positions des pièces d'un joueur"""
        positions = []
        for ligne in range(self.taille):
            for col in range(self.taille):
                pos = Position(ligne, col)
                piece = self.obtenir_piece(pos)
                if ReglesDames.appartient_au_joueur(piece, joueur):
                    positions.append(pos)
        return positions

    def copier(self):
        """Crée une copie du plateau"""
        nouveau_plateau = PlateauDames(self.taille)
        nouveau_plateau.plateau = copy.deepcopy(self.plateau)
        return nouveau_plateau


class MoteurLogique:
    """Moteur logique pour générer et valider les mouvements"""

    def __init__(self, plateau: PlateauDames):
        self.plateau = plateau

    def mouvements_valides_piece(self, pos: Position, joueur: Joueur) -> List[Mouvement]:
        """Génère tous les mouvements valides pour une pièce donnée"""
        piece = self.plateau.obtenir_piece(pos)

        if not ReglesDames.appartient_au_joueur(piece, joueur):
            return []

        # Vérifier d'abord les captures obligatoires
        captures = self._generer_captures_piece(pos, joueur)
        if captures:
            return captures

        # Sinon, mouvements simples
        return self._generer_mouvements_simples(pos, joueur)

    def _generer_mouvements_simples(self, pos: Position, joueur: Joueur) -> List[Mouvement]:
        """Génère les mouvements simples (sans capture)"""
        piece = self.plateau.obtenir_piece(pos)
        mouvements = []

        # Déterminer les directions selon le type de pièce
        if ReglesDames.est_dame(piece):
            directions = ReglesDames.directions_mouvement_dame()
            # Les dames peuvent se déplacer sur plusieurs cases
            for dl, dc in directions:
                distance = 1
                while True:
                    nouvelle_pos = Position(pos.ligne + dl * distance, pos.colonne + dc * distance)

                    if not (ReglesDames.est_position_valide(nouvelle_pos, self.plateau.taille) and
                            ReglesDames.est_case_jouable(nouvelle_pos)):
                        break

                    piece_destination = self.plateau.obtenir_piece(nouvelle_pos)
                    if piece_destination == PieceType.EMPTY:
                        mouvements.append(Mouvement(pos, nouvelle_pos))
                        distance += 1
                    else:
                        break  # Case occupée, arrêter dans cette direction
        else:
            # Pions: mouvement d'une seule case
            directions = ReglesDames.directions_mouvement_pion(joueur)
            for dl, dc in directions:
                nouvelle_pos = Position(pos.ligne + dl, pos.colonne + dc)

                if (ReglesDames.est_position_valide(nouvelle_pos, self.plateau.taille) and
                        ReglesDames.est_case_jouable(nouvelle_pos) and
                        self.plateau.obtenir_piece(nouvelle_pos) == PieceType.EMPTY):
                    mouvements.append(Mouvement(pos, nouvelle_pos))

        return mouvements

    def _generer_captures_piece(self, pos: Position, joueur: Joueur) -> List[Mouvement]:
        """Génère tous les mouvements de capture pour une pièce donnée"""
        captures_simples = self._generer_captures_simples(pos, joueur)
        captures_multiples = []

        # Pour chaque capture simple, vérifier s'il y a des captures multiples possibles
        for capture in captures_simples:
            captures_multiples.extend(self._generer_captures_multiples(capture, joueur, set(capture.captures)))

        # Retourner les captures multiples si elles existent, sinon les captures simples
        return captures_multiples if captures_multiples else captures_simples

    def _generer_captures_simples(self, pos: Position, joueur: Joueur) -> List[Mouvement]:
        """Génère les captures simples pour une pièce"""
        piece = self.plateau.obtenir_piece(pos)
        captures = []

        # Déterminer les directions selon le type de pièce
        if ReglesDames.est_dame(piece):
            directions = ReglesDames.directions_mouvement_dame()
            # Les dames peuvent capturer à distance
            for dl, dc in directions:
                distance = 1
                piece_adversaire_pos = None

                while True:
                    pos_courante = Position(pos.ligne + dl * distance, pos.colonne + dc * distance)

                    if not (ReglesDames.est_position_valide(pos_courante, self.plateau.taille) and
                            ReglesDames.est_case_jouable(pos_courante)):
                        break

                    piece_courante = self.plateau.obtenir_piece(pos_courante)

                    if piece_courante == PieceType.EMPTY:
                        if piece_adversaire_pos is not None:
                            # On a trouvé une case vide après une pièce adversaire
                            captures.append(Mouvement(pos, pos_courante, [piece_adversaire_pos]))
                        distance += 1
                    elif ReglesDames.est_adversaire(piece_courante, joueur):
                        if piece_adversaire_pos is None:
                            piece_adversaire_pos = pos_courante
                            distance += 1
                        else:
                            # Deuxième pièce adversaire dans la même direction
                            break
                    else:
                        # Pièce alliée
                        break
        else:
            # Pions: capture simple adjacente
            directions = ReglesDames.directions_mouvement_pion(joueur)
            for dl, dc in directions:
                # Position de la pièce adversaire
                pos_adversaire = Position(pos.ligne + dl, pos.colonne + dc)
                # Position d'atterrissage après capture
                pos_atterrissage = Position(pos.ligne + 2 * dl, pos.colonne + 2 * dc)

                if (ReglesDames.est_position_valide(pos_adversaire, self.plateau.taille) and
                        ReglesDames.est_position_valide(pos_atterrissage, self.plateau.taille) and
                        ReglesDames.est_case_jouable(pos_atterrissage)):

                    piece_adversaire = self.plateau.obtenir_piece(pos_adversaire)
                    piece_atterrissage = self.plateau.obtenir_piece(pos_atterrissage)

                    if (ReglesDames.est_adversaire(piece_adversaire, joueur) and
                            piece_atterrissage == PieceType.EMPTY):
                        captures.append(Mouvement(pos, pos_atterrissage, [pos_adversaire]))

        return captures

    def _generer_captures_multiples(self, mouvement_initial: Mouvement, joueur: Joueur, captures_deja_faites: Set[Position]) -> List[Mouvement]:
        """Génère les captures multiples à partir d'un mouvement de capture"""
        captures_multiples = []

        # Créer un plateau temporaire pour simuler la capture
        plateau_temp = self.plateau.copier()
        moteur_temp = MoteurLogique(plateau_temp)

        # Exécuter la capture initiale
        piece_originale = plateau_temp.obtenir_piece(mouvement_initial.debut)
        plateau_temp.placer_piece(mouvement_initial.debut, PieceType.EMPTY)

        # Supprimer les pièces capturées
        for pos_capture in mouvement_initial.captures:
            plateau_temp.placer_piece(pos_capture, PieceType.EMPTY)

        # Gérer la promotion en dame
        nouvelle_piece = piece_originale
        if ReglesDames.doit_devenir_dame(mouvement_initial.fin, piece_originale):
            if joueur == Joueur.BLANC:
                nouvelle_piece = PieceType.DAME_BLANCHE
            else:
                nouvelle_piece = PieceType.DAME_NOIRE

        plateau_temp.placer_piece(mouvement_initial.fin, nouvelle_piece)

        # Chercher d'autres captures possibles depuis la nouvelle position
        captures_suivantes = moteur_temp._generer_captures_simples(mouvement_initial.fin, joueur)

        # Filtrer les captures qui concernent des pièces déjà capturées
        captures_valides = []
        for capture in captures_suivantes:
            capture_valide = True
            for pos_capture in capture.captures:
                if pos_capture in captures_deja_faites:
                    capture_valide = False
                    break
            if capture_valide:
                captures_valides.append(capture)

        if not captures_valides:
            # Pas d'autres captures, retourner le mouvement actuel
            return [mouvement_initial]

        # Il y a d'autres captures possibles, les explorer récursivement
        for capture_suivante in captures_valides:
            nouvelles_captures = captures_deja_faites | set(capture_suivante.captures)
            mouvement_combine = Mouvement(
                mouvement_initial.debut,
                capture_suivante.fin,
                mouvement_initial.captures + capture_suivante.captures
            )

            # Récursion pour chercher encore d'autres captures
            moteur_temp.plateau = plateau_temp
            captures_recursives = moteur_temp._generer_captures_multiples(
                mouvement_combine, joueur, nouvelles_captures
            )
            captures_multiples.extend(captures_recursives)

        return captures_multiples if captures_multiples else [mouvement_initial]

    def tous_mouvements_valides(self, joueur: Joueur) -> List[Mouvement]:
        """Génère tous les mouvements valides pour un joueur"""
        tous_mouvements = []
        positions = self.plateau.obtenir_positions_joueur(joueur)

        # Vérifier d'abord s'il y a des captures obligatoires
        captures_obligatoires = []
        for pos in positions:
            captures = self._generer_captures_piece(pos, joueur)
            captures_obligatoires.extend(captures)

        if captures_obligatoires:
            return captures_obligatoires

        # Sinon, tous les mouvements simples
        for pos in positions:
            mouvements = self._generer_mouvements_simples(pos, joueur)
            tous_mouvements.extend(mouvements)

        return tous_mouvements

    def executer_mouvement(self, mouvement: Mouvement, joueur: Joueur) -> bool:
        """Exécute un mouvement sur le plateau"""
        piece = self.plateau.obtenir_piece(mouvement.debut)

        if not ReglesDames.appartient_au_joueur(piece, joueur):
            return False

        # Effectuer le mouvement
        self.plateau.placer_piece(mouvement.debut, PieceType.EMPTY)

        # Gérer les captures
        for pos_capture in mouvement.captures:
            self.plateau.placer_piece(pos_capture, PieceType.EMPTY)

        # Placer la pièce à sa nouvelle position
        nouvelle_piece = piece
        if ReglesDames.doit_devenir_dame(mouvement.fin, piece):
            if joueur == Joueur.BLANC:
                nouvelle_piece = PieceType.DAME_BLANCHE
            else:
                nouvelle_piece = PieceType.DAME_NOIRE

        self.plateau.placer_piece(mouvement.fin, nouvelle_piece)
        return True


class MiniMax:
    """Implémentation de l'algorithme MiniMax pour l'IA"""

    def __init__(self, profondeur_max: int = 4):
        self.profondeur_max = profondeur_max

    def evaluer_plateau(self, plateau: PlateauDames, joueur: Joueur) -> float:
        """Fonction d'évaluation du plateau améliorée"""
        score = 0
        pieces_blanc = 0
        pieces_noir = 0
        dames_blanc = 0
        dames_noir = 0

        for ligne in range(plateau.taille):
            for col in range(plateau.taille):
                piece = plateau.obtenir_piece(Position(ligne, col))

                if piece == PieceType.PION_BLANC:
                    pieces_blanc += 1
                    # Bonus pour avancer vers la promotion
                    score += 1 + (7 - ligne) * 0.1 if joueur == Joueur.BLANC else -1 - (7 - ligne) * 0.1
                elif piece == PieceType.PION_NOIR:
                    pieces_noir += 1
                    # Bonus pour avancer vers la promotion
                    score += 1 + ligne * 0.1 if joueur == Joueur.NOIR else -1 - ligne * 0.1
                elif piece == PieceType.DAME_BLANCHE:
                    dames_blanc += 1
                    score += 3 if joueur == Joueur.BLANC else -3
                elif piece == PieceType.DAME_NOIRE:
                    dames_noir += 1
                    score += 3 if joueur == Joueur.NOIR else -3

        # Bonus pour avoir plus de dames
        if joueur == Joueur.BLANC:
            score += (dames_blanc - dames_noir) * 0.5
        else:
            score += (dames_noir - dames_blanc) * 0.5

        return score

    def minimax(self, plateau: PlateauDames, profondeur: int, maximisant: bool,
                joueur: Joueur, alpha: float = -math.inf, beta: float = math.inf,
                joueur_racine: Optional[Joueur] = None) -> Tuple[float, Optional[Mouvement]]:
        """Algorithme MiniMax avec élagage alpha-beta"""
        # Conserver le point de vue du joueur racine pendant toute la récursion.
        # La version universitaire alternait aussi le point de vue de la fonction
        # d'évaluation, ce qui rendait les scores incohérents entre deux niveaux.
        if joueur_racine is None:
            joueur_racine = joueur

        moteur = MoteurLogique(plateau)
        mouvements = moteur.tous_mouvements_valides(joueur)

        if profondeur == 0 or not mouvements:
            return self.evaluer_plateau(plateau, joueur_racine), None

        meilleur_mouvement = None

        if maximisant:
            max_eval = -math.inf
            for mouvement in mouvements:
                nouveau_plateau = plateau.copier()
                nouveau_moteur = MoteurLogique(nouveau_plateau)
                nouveau_moteur.executer_mouvement(mouvement, joueur)

                adversaire = Joueur.NOIR if joueur == Joueur.BLANC else Joueur.BLANC
                eval_score, _ = self.minimax(
                    nouveau_plateau, profondeur - 1, False, adversaire,
                    alpha, beta, joueur_racine
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                    meilleur_mouvement = mouvement

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break

            return max_eval, meilleur_mouvement
        else:
            min_eval = math.inf
            for mouvement in mouvements:
                nouveau_plateau = plateau.copier()
                nouveau_moteur = MoteurLogique(nouveau_plateau)
                nouveau_moteur.executer_mouvement(mouvement, joueur)

                adversaire = Joueur.NOIR if joueur == Joueur.BLANC else Joueur.BLANC
                eval_score, _ = self.minimax(
                    nouveau_plateau, profondeur - 1, True, adversaire,
                    alpha, beta, joueur_racine
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    meilleur_mouvement = mouvement

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break

            return min_eval, meilleur_mouvement


class JeuDames:
    """Classe principale du jeu de dames"""

    def __init__(self):
        self.plateau = PlateauDames()
        self.moteur = MoteurLogique(self.plateau)
        self.minimax = MiniMax()
        self.joueur_actuel = Joueur.BLANC
        self.mode_ia = True

    def afficher_plateau(self):
        """Affiche le plateau de jeu"""
        print("\n   ", end="")
        for i in range(8):
            print(f" {i} ", end="")
        print()

        for ligne in range(8):
            print(f"{ligne}  ", end="")
            for col in range(8):
                piece = self.plateau.obtenir_piece(Position(ligne, col))

                if (ligne + col) % 2 == 0:  # Case blanche
                    symbole = "░░░"
                else:  # Case noire
                    if piece == PieceType.EMPTY:
                        symbole = "   "
                    elif piece == PieceType.PION_BLANC:
                        symbole = " ○ "
                    elif piece == PieceType.PION_NOIR:
                        symbole = " ● "
                    elif piece == PieceType.DAME_BLANCHE:
                        symbole = " ♛ "
                    elif piece == PieceType.DAME_NOIRE:
                        symbole = " ♜ "
                    else:
                        symbole = "   "

                print(symbole, end="")
            print()
        print()

    def afficher_mouvements_valides(self, mouvements: List[Mouvement]):
        """Affiche la liste des mouvements valides"""
        if not mouvements:
            print("Aucun mouvement valide disponible!")
            return

        print("Mouvements valides:")
        for i, mouv in enumerate(mouvements):
            if mouv.captures:
                if len(mouv.captures) == 1:
                    capture_text = f" (capture 1 pièce)"
                else:
                    capture_text = f" (capture multiple: {len(mouv.captures)} pièces)"
            else:
                capture_text = ""

            print(
                f"{i + 1}. De ({mouv.debut.ligne},{mouv.debut.colonne}) vers ({mouv.fin.ligne},{mouv.fin.colonne}){capture_text}")

    def saisir_mouvement_joueur(self, mouvements: List[Mouvement]) -> Optional[Mouvement]:
        """Permet au joueur de saisir son mouvement"""
        self.afficher_mouvements_valides(mouvements)

        try:
            choix = input(
                f"\nJoueur {self.joueur_actuel.name}, choisissez votre mouvement (1-{len(mouvements)}) ou 'q' pour quitter: ")

            if choix.lower() == 'q':
                return None

            index = int(choix) - 1
            if 0 <= index < len(mouvements):
                return mouvements[index]
            else:
                print("Choix invalide!")
                return self.saisir_mouvement_joueur(mouvements)

        except ValueError:
            print("Veuillez entrer un nombre valide!")
            return self.saisir_mouvement_joueur(mouvements)

    def verifier_fin_jeu(self) -> Optional[Joueur]:
        """Vérifie si le jeu est terminé et retourne le gagnant"""
        mouvements_blanc = self.moteur.tous_mouvements_valides(Joueur.BLANC)
        mouvements_noir = self.moteur.tous_mouvements_valides(Joueur.NOIR)

        if not mouvements_blanc:
            return Joueur.NOIR
        elif not mouvements_noir:
            return Joueur.BLANC

        return None

    def jouer_tour(self) -> bool:
        """Joue un tour complet, retourne False si le jeu doit s'arrêter"""
        print(f"\n=== Tour du joueur {self.joueur_actuel.name} ===")
        self.afficher_plateau()

        # Vérifier fin de jeu
        gagnant = self.verifier_fin_jeu()
        if gagnant:
            print(f"\n🎉 Jeu terminé! Le gagnant est: {gagnant.name}")
            return False

        # Obtenir les mouvements valides
        mouvements = self.moteur.tous_mouvements_valides(self.joueur_actuel)

        if not mouvements:
            print(f"Aucun mouvement possible pour {self.joueur_actuel.name}")
            return False

        # Déterminer le mouvement à jouer
        if self.mode_ia and self.joueur_actuel == Joueur.NOIR:
            print("L'IA réfléchit...")
            _, mouvement = self.minimax.minimax(self.plateau, self.minimax.profondeur_max, True, self.joueur_actuel)

            capture_info = ""
            if mouvement.captures:
                if len(mouvement.captures) == 1:
                    capture_info = " (capture 1 pièce)"
                else:
                    capture_info = f" (capture {len(mouvement.captures)} pièces)"

            print(
                f"L'IA joue: De ({mouvement.debut.ligne},{mouvement.debut.colonne}) vers ({mouvement.fin.ligne},{mouvement.fin.colonne}){capture_info}")
        else:
            mouvement = self.saisir_mouvement_joueur(mouvements)
            if mouvement is None:  # Joueur veut quitter
                return False

        # Exécuter le mouvement
        if self.moteur.executer_mouvement(mouvement, self.joueur_actuel):
            print(f"Mouvement exécuté avec succès!")
            if mouvement.captures:
                if len(mouvement.captures) == 1:
                    print(f"Pièce capturée!")
                else:
                    print(f"Capture multiple: {len(mouvement.captures)} pièces capturées!")

        # Changer de joueur
        self.joueur_actuel = Joueur.NOIR if self.joueur_actuel == Joueur.BLANC else Joueur.BLANC

        return True

    def demarrer_partie(self):
        """Démarre une nouvelle partie"""
        print("🎯 Bienvenue au Jeu de Dames!")

        choix_mode = input("\nChoisissez le mode de jeu:\n1. Joueur vs IA\n2. Joueur vs Joueur\nVotre choix (1-2): ")
        self.mode_ia = choix_mode != "2"

        if self.mode_ia:
            print("Mode: Joueur (BLANC) vs IA (NOIR)")
        else:
            print("Mode: Joueur vs Joueur")

        # Boucle principale du jeu
        while self.jouer_tour():
            pass

        print("\nMerci d'avoir joué! 🎮")


def main():
    """Point d'entrée principal"""
    jeu = JeuDames()
    jeu.demarrer_partie()


if __name__ == "__main__":
    main()
