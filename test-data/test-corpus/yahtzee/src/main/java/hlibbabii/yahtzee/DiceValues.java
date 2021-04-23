package hlibbabii.yahtzee;

import java.util.Iterator;

public class DiceValues implements Iterable<Integer> {

    public static final Integer MIN_DICE_VALUE = 1;
    public static final Integer MAX_DICE_VALUE = 6;

    private Iterator<Integer> iterator;

    public DiceValues(Iterator<Integer> iterator) {
        this.iterator = iterator;
    }

    public static Iterable<? extends Integer> getDescendingIterator() {
        return new DiceValues(new DescendingIterator());
    }

    public static class DescendingIterator implements Iterator<Integer> {

        private Integer currentValue = MAX_DICE_VALUE;

        @Override
        public boolean hasNext() {
            return this.currentValue >= MIN_DICE_VALUE;
        }

        @Override
        public Integer next() {
            return this.currentValue--;
        }
    }

    @Override
    public Iterator<Integer> iterator() {
        return this.iterator;
    }
}
