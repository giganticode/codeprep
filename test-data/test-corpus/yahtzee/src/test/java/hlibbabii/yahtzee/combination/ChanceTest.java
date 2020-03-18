package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ChanceTest {
    @Test
    void testChance() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,3,3,6,6);
        int actual = Chance.CHANCE.earnedScores(diceLayout);
        assertEquals(19, actual);
    }
}