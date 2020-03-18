package hlibbabii.yahtzee.model;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class DiceLayoutTest {

    @Test
    void testEmpty() {
        DiceLayout diceLayout = DiceLayout.empty();

        assertEquals(0, diceLayout.toCounts().entrySet().size());
    }

    @Test
    void testFromNumbers() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,2,3,4,4);

        int[] numbers = diceLayout.toSortedNumbers();
        Map<Integer, Integer> counts = diceLayout.toCounts();
    }

}