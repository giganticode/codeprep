package hlibbabii.yahtzee.model;

import hlibbabii.yahtzee.DiceValues;
import hlibbabii.yahtzee.gameplay.Game;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class DiceLayout {

    private static final String INVALID_DICE_LAYOUT_MESSAGE_TEMPLATE = "Invalid dice layout: %s. %s";

    private SortedMap<Integer, Integer> valuesToOccurences;

    private DiceLayout(SortedMap<Integer, Integer> valuesToOccurences) {
        this.valuesToOccurences = valuesToOccurences;

        this.checkAlignmentInvariants(valuesToOccurences);
    }

    private void checkAlignmentInvariants(Map<Integer, Integer> valuesToOccurences) {
        if (this.getSize() > Game.N_DICE) {
            String reason = String.format("The number of dice cannot be more than %s.", Game.N_DICE);
            throw new IllegalArgumentException(String.format(INVALID_DICE_LAYOUT_MESSAGE_TEMPLATE, Arrays.toString(this.toSortedNumbers()), reason));
        }
        for (Integer rolledNumber : valuesToOccurences.keySet()) {
            if (rolledNumber < DiceValues.MIN_DICE_VALUE || rolledNumber > DiceValues.MAX_DICE_VALUE) {
                String reason = "Rolled numbers contain invalid values.";
                throw new IllegalArgumentException(String.format(INVALID_DICE_LAYOUT_MESSAGE_TEMPLATE, Arrays.toString(this.toSortedNumbers()), reason));
            }
        }
    }

    /* Dice layout creation options */

    public static DiceLayout empty() {
        return new DiceLayout(new TreeMap<>());
    }

    public static DiceLayout fromMap(SortedMap<Integer, Integer> valuesToOccurences) {
        return new DiceLayout(valuesToOccurences);
    }

    private static DiceLayout fromStream(Stream<Integer> stream) {
        return DiceLayout.fromMap(new TreeMap<>(
                stream.collect(Collectors.groupingBy((a) -> a, Collectors.summingInt((e)->1)))
        ));
    }

    public static DiceLayout fromNumbers(int... numbers) {
        return fromStream(IntStream.of(numbers).boxed());
    }

    public static DiceLayout fromNumbers(List<Integer> rolledNumbers) {
        return fromStream(rolledNumbers.stream());
    }

    /* Dice layout representation options */

    public Map<Integer, Integer> toCounts() {
        return this.valuesToOccurences;
    }

    public int getCount(int number) {
        return toCounts().getOrDefault(number, 0);
    }

    public int[] toSortedNumbers() {
        return this.valuesToOccurences.entrySet().stream()
                .flatMapToInt((a) -> IntStream.range(0, a.getValue()).map((k) -> a.getKey())).toArray();
    }

    /* */

    public int getSize() {
        return this.valuesToOccurences.values().stream().mapToInt(e -> e).sum();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || this.getClass() != o.getClass()) return false;
        DiceLayout that = (DiceLayout) o;
        return Objects.equals(this.valuesToOccurences, that.valuesToOccurences);
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.valuesToOccurences);
    }

    @Override
    public String toString() {
        return "DiceLayout{" +
                "valuesToOccurences=" + Arrays.toString(this.toSortedNumbers()) +
                '}';
    }
}