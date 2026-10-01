# Checkers Game with Logic Rules – Python

![SEARCH & LOGIC — Checkers, Minimax and alpha-beta pruning](assets/portfolio-banner.svg)

Console-based academic checkers game implemented with Python classes and a Minimax opponent using alpha-beta pruning.

## Features

- 8×8 board initialization with 24 pieces.
- Playable-square and ownership rules.
- Simple diagonal moves, mandatory capture selection, multiple-capture generation, and promotion.
- Long-range movement and capture for kings.
- Human-versus-human and human-versus-AI console modes.
- Position evaluation and depth-limited Minimax with alpha-beta pruning.



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


## Tests, results and limitations

The academic report documents:

- unit tests for the core classes and game engine;
- integration tests after assembling the complete game;
- AI tests against a human player in different game situations;
- performance tests at different Minimax search depths;
- playability and user-experience tests.

The report concludes that the Minimax AI performs well at several search depths, with **depth 4** providing a good balance between competitiveness and responsiveness. Greater depths strengthen the AI but increase computation time.

The limitations identified in the report are the growth in response time as search depth increases and the difficulty of handling some strategically complex positions. The proposed improvements are stronger alpha-beta optimization and richer evaluation heuristics.
