from typing import List

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer

from dataprep.model.core import ParsedToken
from dataprep.parse import matchers
from dataprep.parse.matchers import DefaultMatcher

matchers = [
    matchers.NewLineMatcher(),
    matchers.TabMatcher(),
    matchers.WhitespaceMatcher(),
    matchers.OperatorMatcher(),
    matchers.NumberMatchers(),
    matchers.WordMatcher(),
    matchers.KeywordMatcher(),
    matchers.StringMatcher(),
    matchers.CommentMatcher(),
]


def _convert(token, value: str) -> List[ParsedToken]:
    for matcher in matchers:
        if matcher.match(token, value):
            return matcher.transform(value)

    if DefaultMatcher().match(token, value):
        return DefaultMatcher().transform(value)

    assert False


def convert_text(text: str, extension: str=None) -> List[ParsedToken]:
    lexer = get_lexer_by_name(extension) if extension else guess_lexer(text)
    for token, value in lex(repr(text)[1:-1], lexer):
        model_tokens = _convert(token, value)
        print(f'token: {token}, value: {value}')
        for mr in model_tokens:
            yield mr


# model_tokens_gen = convert_to_model('''
# package hlibbabii.yahtzee.gameplay;
#
# import hlibbabii.yahtzee.player.DummyPlayer;
# import hlibbabii.yahtzee.Player;
# import hlibbabii.yahtzee.model.DiceLayout;
# import hlibbabii.yahtzee.combination.Combination;
# import hlibbabii.yahtzee.util.RandomService;
#
# import java.util.*;
# import java.util.Map.Entry;
#
# public class Game {
#
#     public static final int N_DICE = 5;
#     private static final Integer NUMBER_OF_ATTEMPTS = 3;
#
#     private final Player player1;
#     private final Player player2;
#     private final GameStats gameStats;
#
#
#     public Game(Player player1, Player player2) {
#         this.player1 = player1;
#         this.player2 = player2;
#         this.gameStats = new GameStats(player1, player2);
#     }
#
#     public static void main(String[] args) {
#         GameStats gameStats = new Game(new DummyPlayer(), new DummyPlayer()).play();
#         System.out.println(gameStats.getFinalPoints());
#     }
#
#     public GameStats play() {
#         while (this.gameStats.combinationsAvailable()) {
#             MoveResult moveResult1 = this.makeMove(this.player1);
#             this.gameStats.addMoveResult(moveResult1);
#
#             MoveResult moveResult2 = this.makeMove(this.player2);
#             this.gameStats.addMoveResult(moveResult2);
#         }
#         return this.gameStats;
#     }
#
#     private MoveResult makeMove(Player player) {
#         PlayerStats playerStats = this.gameStats.getPlayerStats(player);
#         Set<Combination> availableCombinations = playerStats.getAvailableCombinations();
#
#         DiceLayout fixedDiceLayout = DiceLayout.empty();
#         int howManyToRoll = N_DICE;
#         for (int i = NUMBER_OF_ATTEMPTS; i > 0; i--) {
#             DiceLayout nonFixedDiceLayout = this.roll(howManyToRoll);
#             Decision decision;
#             try {
#                  decision = player.makeDecision(nonFixedDiceLayout, fixedDiceLayout, availableCombinations, i - 1);
#             } catch (Exception e) {
#                 throw new PlayerException(e);
#             }
#             if (decision.isCombinationDecision()) {
#                 return MoveResult.create(player, decision, nonFixedDiceLayout);
#             } else {
#                 DiceLayout currentFixedDiceLayout = decision.getDiceDecidedToLeave();
#                 this.checkFixedDiceLayoutValid(currentFixedDiceLayout, fixedDiceLayout);
#                 fixedDiceLayout = currentFixedDiceLayout;
#                 howManyToRoll = N_DICE - fixedDiceLayout.getSize();
#             }
#         }
#         throw new AssertionError("Combination decision should have already been made!");
#     }
#
#     private void checkFixedDiceLayoutValid(DiceLayout newFixedDiceLayout, DiceLayout previousFixedDiceLayout) {
#         for (Entry<Integer, Integer> previousAlignmentEntry: previousFixedDiceLayout.toCounts().entrySet()) {
#             if (previousAlignmentEntry.getValue() > newFixedDiceLayout.toCounts().get(previousAlignmentEntry.getKey())) {
#                 throw new AssertionError("The dice which once were left on the table cannot be rerolled later");
#             }
#         }
#     }
#
#     public DiceLayout roll() {
#         return this.roll(N_DICE);
#     }
#
#     private DiceLayout roll(int howMany) {
#         RandomService random = new RandomService();
#         int[] arr = new int[howMany];
#         for (int i = 0; i < howMany; i++) {
#             arr[i] = random.getRandomDiceNumber();
#         }
#         return DiceLayout.fromNumbers(arr);
#     }
# }
# ''')
#
# for i in simple_split(model_tokens_gen):
#     print(f"{i}")