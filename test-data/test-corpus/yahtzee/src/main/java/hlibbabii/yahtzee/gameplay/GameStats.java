package hlibbabii.yahtzee.gameplay;

import hlibbabii.yahtzee.Player;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

public class GameStats {
    Map<Player, PlayerStats> playerStatsMap;

    public GameStats(Player player1, Player player2) {
        this.playerStatsMap = new HashMap<Player, PlayerStats>() {{
            this.put(player1, new PlayerStats());
            this.put(player2, new PlayerStats());
        }};
    }

    public boolean combinationsAvailable() {
        PlayerStats anyPlayerStats = this.playerStatsMap.values().iterator().next();
        return !anyPlayerStats.getAvailableCombinations().isEmpty();
    }

    public void addMoveResult(MoveResult moveResult) {
        Player player = moveResult.getPlayer();
        PlayerStats playerStats = this.playerStatsMap.get(player);
        playerStats.put(moveResult.getCombination(), moveResult.getScore());
    }

    public PlayerStats getPlayerStats(Player player) {
        return this.playerStatsMap.get(player);
    }

    public Map<Player, Integer> getFinalPoints() {
        return this.playerStatsMap.entrySet().stream()
                .collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue().getFinalPoints()));
    }
}
