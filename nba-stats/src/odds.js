import React from "react";
import './App.css';
import { useEffect, useState } from "react";
import { Box } from "@mui/material";
import { Link } from "react-router-dom";

function Odds() {

    const [games, setGames] = useState([])
    const [gameOdds, setGameOdds] = useState([])
    const [selectedGame, setSelectedGame] = useState()
    const [playerProps, setPlayerProps] = useState([])
    const [currentGameProp, setCurrentGameProp] = useState("h2h")
    const [currentPlayerMarket, setCurrentPlayerMarket] = useState("player_points")
    const [selectedBookmaker, setSelectedBookmaker] = useState(null);
    const BACKEND_URL = 'https://nba-predictor-9f7k.onrender.com'


// FETCH UPCOMING GAMES --------------------------------
    useEffect(() => {

        async function fetchGames() {
          const response = await fetch(`${BACKEND_URL}/games`)
          const data = await response.json()
          // console.log(data)
          setGames(Object.entries(data).map(([name, id]) => ({ name, id })))
        }    
        fetchGames()
      }, [BACKEND_URL])

// FETCH UPCOMING GAMES PROP ODDS --------------------------------
      async function fetchGameOdds(oddsId, marketId) {
        const response = await fetch(`${BACKEND_URL}/odds?odds_id=${oddsId}&market_id=${marketId}`)
        const data = await response.json()

        const formattedGameOdds = Object.entries(data).map(([bookmaker, lines]) => ({
            bookmaker,
            lines: Object.entries(lines).map(([team, details]) => ({
              team,
              ...details,
            })),
          }));

        setGameOdds(formattedGameOdds);
      }

// FETCH UPCOMING PLAYER PROPS --------------------------------
      async function fetchPlayerProps(oddsId, playerPropMarket) {
        const response = await fetch(`${BACKEND_URL}/playerprops?odds_id=${oddsId}&player_prop_market=${playerPropMarket}`)
        const data = await response.json()
        
        const formattedProps = Object.entries(data).map(([bookmaker, markets]) => ({bookmaker,
            playerProps:markets[playerPropMarket] || [],
        }))
        setPlayerProps(formattedProps)
    }

    return (
        <div className="background">

        {/* NAVBAR  */}
        <Box 
            sx={{
                width: '100%',
                bgcolor: 'rgba(48, 48, 60, 0.95)', 
                borderBottom: '1px solid rgba(255, 255, 255, 0.25)', 
                borderRadius: '10px',
                boxShadow: '0 10px 20px rgba(0, 0, 0, 0.5)', 
                backdropFilter: 'blur(10px)', 
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: { xs: '10px 0', sm: '20px 0' },
                position: 'sticky',
                top: 5,
                zIndex: 10,
            }}>
            <Box 
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    width: '90%',
                    maxWidth: '1200px',
                }}>
                <Link 
                    to={'/players'} 
                    style={{
                        textDecoration: 'none',
                        color: '#58a6ff',
                        fontSize: '1rem',
                        fontWeight: '500',
                        border: '2px solid rgba(88, 166, 255, 0.6)',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        transition: 'all 0.3s ease',
                        textShadow: '0 2px 6px rgba(88, 166, 255, 0.4)',
                        position: 'relative',
                        overflow: 'hidden',
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.color = '#f0f0f0';
                        e.target.style.backgroundColor = '#58a6ff';
                        e.target.style.boxShadow = '0 4px 15px rgba(88, 166, 255, 0.6)';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.color = '#58a6ff';
                        e.target.style.backgroundColor = 'transparent';
                        e.target.style.boxShadow = 'none';
                    }}
                    >
                    Players
                </Link>
                <h2 
                    style={{
                        margin: 0,
                        fontSize: { xs: '1.5rem', sm: '2rem' },
                        color: '#f4f4f4',
                        fontWeight: 'bold',
                        textShadow: '0 4px 10px rgba(255, 255, 255, 0.5)',
                    }}>
                    Odds
                </h2>
                <Link 
                    to={'/predictor'} 
                    style={{
                        textDecoration: 'none',
                        color: '#58a6ff',
                        fontSize: '1rem',
                        fontWeight: '500',
                        border: '2px solid rgba(88, 166, 255, 0.6)',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        transition: 'all 0.3s ease',
                        textShadow: '0 2px 6px rgba(88, 166, 255, 0.4)',
                        position: 'relative',
                        overflow: 'hidden',
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.color = '#f0f0f0';
                        e.target.style.backgroundColor = '#58a6ff';
                        e.target.style.boxShadow = '0 4px 15px rgba(88, 166, 255, 0.6)';
                        }}
                    onMouseLeave={(e) => {
                        e.target.style.color = '#58a6ff';
                        e.target.style.backgroundColor = 'transparent';
                        e.target.style.boxShadow = 'none';
                        }}
        >
                    Point Predictor
                </Link>
            </Box>
        </Box>
        

    <Box sx={{ padding: '20px' }}>
    {/* Game List */}
    <Box className="game-list">
        {games.map((game) => (
            <button
                key={game.id}
                className={`game-button ${selectedGame?.id === game.id ? 'selected-game' : ''}`}
                onClick={() => {
                    fetchGameOdds(game.id, "h2h");
                    fetchPlayerProps(game.id, "player_points");
                    setSelectedGame(game);
                    setCurrentGameProp("h2h");
                    setCurrentPlayerMarket("player_points");
                }}
            >
                {game.name}
            </button>
        ))}
    </Box>

    {/* Game Details */}
    {selectedGame && (
        <Box>
            <h3 style={{ textAlign: 'center', color: '#f4f4f4', fontSize: '1.5rem' }}>{selectedGame.name}</h3>
            <Box className="tab-buttons">
                {["h2h", "spreads", "totals"].map((prop) => (
                    <button
                        key={prop}
                        className={`tab-button ${currentGameProp === prop ? 'active' : ''}`}
                        onClick={() => {
                            fetchGameOdds(selectedGame.id, prop);
                            setCurrentGameProp(prop);
                        }}
                    >
                        {prop === "h2h" ? "Money Line" : prop.charAt(0).toUpperCase() + prop.slice(1)}
                    </button>
                ))}
            </Box>

            {/* Game Odds */}
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                    gap: 2,
                    marginTop: 4,
                    '@media (max-width: 768px)': {
                        gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', 
                    },
                }} >
                {gameOdds.map((odd, index) => (
                    <Box
                        key={index}
                        sx={{
                            bgcolor: 'rgba(30, 30, 47, 0.9)',
                            borderRadius: 2,
                            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.75)',
                            padding: 3,
                            color: '#fff',
                            textAlign: 'center',
                        }}>
                        <strong>{odd.bookmaker}</strong>
                        <Box
                            sx={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                                gap: 2,
                                marginTop: 2,
                                '@media (max-width: 768px)': {
                                    gridTemplateColumns: '1fr', 
                                },
                            }}>
                            {odd.lines.map((line, i) => (
                                <Box
                                    key={i}
                                    sx={{
                                        padding: 2,
                                        borderRadius: 2,
                                        bgcolor: '#333',
                                        color: '#fff',
                                        textAlign: 'center',
                                        border: '1px solid rgba(255, 255, 255, 0.1)',
                                    }}>
                                    <strong>{line.team}</strong>
                                    <div>Odds: {line.Price}</div>
                                    {line.Market !== "h2h" && <div>Value: {line.Value}</div>}
                                </Box>
                            ))}
                        </Box>
                    </Box>
                ))}
            </Box>
        </Box>
    )}

    {/* Player Props */}
    {selectedGame && (
        <Box>
            {/* Points, Assists, Rebounds Options */}
            <Box
                sx={{
                    display: 'flex',
                    gap: 2,
                    justifyContent: 'center',
                    margin: 5,
                    '@media (max-width: 768px)': {
                        flexDirection: 'column', 
                    },
                }}
            >
                {["player_points", "player_assists", "player_rebounds"].map((market) =>  (
                    <button
                        key={market}
                        className={`tab-button ${currentPlayerMarket === market ? 'active' : ''}`}
                        onClick={() => {
                            setCurrentPlayerMarket(market);
                            fetchPlayerProps(selectedGame.id, market);
                        }}
                        style={{
                            padding: '8px 16px',
                            borderRadius: '4px',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#fff',
                        }}
                    >
                        {market.replace("player_", "").toUpperCase()}
                    </button>
                ))}
            </Box>

            {/* Bookmaker Toggle Buttons */}
            <Box
                sx={{
                    display: 'flex',
                    gap: 2,
                    justifyContent: 'center',
                    marginBottom: 2,
                    '@media (max-width: 768px)': {
                        flexDirection: 'column',                    
                    },
                }}
            >
                {playerProps.map((bookmaker) => (
                    <button
                        key={bookmaker.bookmaker}
                        onClick={() => setSelectedBookmaker(selectedBookmaker === bookmaker.bookmaker ? null : bookmaker.bookmaker)}
                        style={{
                            backgroundColor: selectedBookmaker === bookmaker.bookmaker ? '#58a6ff' : '#333',
                            padding: '8px 16px',
                            borderRadius: '5px',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#fff',
                            flexGrow: 1,
                            boxShadow: '0 4px 15px rgba(0, 0, 0, 1)'
                        }}>
                        {bookmaker.bookmaker}
                    </button>
                ))}
            </Box>

            {/* Player Props - Displaying Data Only for the Selected Bookmaker */}
            {selectedBookmaker && (
                <Box
                    sx={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(20%, 1fr))',
                        gap: 2,
                        '@media (max-width: 768px)': {
                            gridTemplateColumns:  'repeat(auto-fill, minmax(40%, 1fr))'
                        },
                    }}
                >
                    {playerProps
                        .find((bookmaker) => bookmaker.bookmaker === selectedBookmaker)
                        ?.playerProps.map((prop, i) => (
                            <Box
                                key={i}
                                sx={{
                                    padding: 2,
                                    borderRadius: 2,
                                    bgcolor: '#333',
                                    color: '#fff',
                                    textAlign: 'center',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.5)'
                                }}
                            >
                                <strong>{prop.player}</strong>
                                <div>Line: {prop.Line}</div>
                                <div>Value: {prop.Value}</div>
                                <div>Odds: {prop.odds}</div>
                            </Box>
                        ))}
                </Box>
            )}
        </Box>
    )}
</Box>



        </div>
    )
}

export default Odds;