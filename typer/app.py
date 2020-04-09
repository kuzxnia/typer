import logging

from typer.models import Game, GameMenu, GameSummary

logging.basicConfig(
    filename="typer.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)


def run():
    game_menu = GameMenu()
    game_menu.run()
    game = Game(*game_menu.range, game_menu.lang)
    game.run()
    GameSummary(game.periods, game.correct_words, game.incorrect_words).run()
