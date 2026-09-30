# Checkers Game with Logic Rules – Python

Console-based academic checkers game implemented with Python classes and a Minimax opponent using alpha-beta pruning.

## Verified features

- 8×8 board initialization with 24 pieces.
- Playable-square and ownership rules.
- Simple diagonal moves, mandatory capture selection, multiple-capture generation, and promotion.
- Long-range movement and capture for kings.
- Human-versus-human and human-versus-AI console modes.
- Position evaluation and depth-limited Minimax with alpha-beta pruning.

The implementation is a simplified ruleset: men move and capture forward only, while kings are long-range pieces. It should not be presented as a complete implementation of every national or international draughts rule.

## Portfolio correction

The submitted Minimax recursion changed the evaluation perspective at every ply. This copy preserves the French pedagogical names and fixes the recursion by keeping the root player's perspective constant. Regression tests cover board setup, mandatory capture, promotion, and legal AI move selection.

## Requirements and use

Python 3.10+; no third-party packages are required.

```bash
python checkers.py
python -m unittest discover -s tests -v
```

## Authors

- Adam El Akkaoui
- Mohammed Zaidouh

## Academic artefacts

- [French academic report (PDF)](docs/academic-report-fr.pdf)
- [French presentation (PPTX)](presentations/checkers-presentation-fr.pptx)

No video or external dataset was found.

## Testing and limitations

On Python 3.11, four tests passed for initial setup, mandatory capture, promotion and legal Minimax selection; byte-compilation also passed. Full interactive play was not automated. The interface is text-only, and no raw timing data accompanied the report's informal performance/user-test claims. The portfolio correction preserves pedagogical French naming while fixing evaluation from the intended player's perspective.
