import './App.css';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'
import { Box, Paper, CircularProgress, TableRow, TableHead, TableContainer, Table, TableCell, TableBody } from "@mui/material";
import teamDictionary from './teamcodes';



function PredictionModel() {

    const [playerName, setPlayerName] = useState()
    const [players, setPlayers] = useState([])
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [result, setResult] = useState()
    const [error, setError] = useState()
    const [loading, setLoading] = useState(false)
    const apiKey = process.env.REACT_APP_API_KEY;
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;


    const fetchPlayers = async () => {
      try {
          setError("");
          setPlayers([]); // Clear previous results
          setLoading(true);
  
          const response = await axios.get("https://api-nba-v1.p.rapidapi.com/players", {
              params: { search: playerName }, 
              headers: { "x-rapidapi-key": apiKey, "x-rapidapi-host": "api-nba-v1.p.rapidapi.com" }
          });
  
          if (response.data?.response?.length > 0) {
              setPlayers(response.data.response); // Store players list
          } else {
              setError("No players found");
          }
      } catch (err) {
          setError("Error fetching players");
      } finally {
          setLoading(false);
      }
  };

    const fetchPrediction = async (player) => {
      if (!player) {
          setError("Please select a player");
          return;
      }
  
      try {
          setError("");
          setLoading(true);
          setSelectedPlayer(player)
          const response = await axios.get(`${BACKEND_URL}/predict`, {
              params: { player_id: player.id }, 
          });
          setResult(response.data);
      } catch (err) {
          setError(err.response?.data?.error || "An error occurred");
      } finally {
          setLoading(false);
      }
  };

    const handlePlayerSelect = (player) => {
      setSelectedPlayer(player);  
      setResult(null);            
      fetchPrediction(player);    
    };

  
      console.log(result)
      function createData(matchup, date, wl, reb, ast, pts) {
        return { matchup, date, wl, reb, ast, pts };
      }
      
      const createRows = () => {
        if (!result?.recent_games || result.recent_games.length === 0) {
          return []; 
        }
      
        return result.recent_games.slice().reverse().map((game) =>
          createData(
            `${game.opponent}`,
            formatDate(game.game_date.slice(0,10)) || "", 
            game.result || "Underway",  
            game.rebounds || "0", 
            game.assists || "0",  
            game.points || "0"  
          )
        );
      };
      
      const rows = createRows();
      const pointsArray = result?.recent_games?.map((game) => Number(game.points)) || [];
      const averagePointsArray = pointsArray[0]+pointsArray[1]+pointsArray[2]+pointsArray[3]+pointsArray[4]
      const averagePoints = averagePointsArray/5

      function getTeamName(teamCode) {
        return teamDictionary[teamCode] || teamCode; 
      }

      function formatDate(dateString) {
        const date = new Date(dateString);
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const month = months[date.getMonth()];
        const day = date.getDate();
        
        return `${month} ${day}`;
      }
      

return (
    <div className='background'>

{/* NAVBAR */}
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
                fontSize: { xs: '1.5rem', sm: '2rem'},
                color: '#f4f4f4',
                fontWeight: 'bold',
                textAlign: 'center',
                textShadow: '0 4px 10px rgba(255, 255, 255, 0.5)',
            }}>
            Point Predictor
        </h2>
        <Link 
            to={'/odds'} 
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
            Odds
        </Link>
    </Box>
</Box>

{/* ABOUT MESSAGE */}
<div className='predictor-textbox'>
    <p>
        <span style={{ fontWeight: 'bold', fontSize: '1.2rem', color: '#2e9cca' }}> Welcome To The Point Predictor! </span> 
        When predicting player performance, two key factors stand out: recent performance trends and the strength of the upcoming opponent. We leveraged these variables to design our software, which uses this data to generate a highly accurate, mathematically-driven estimate of a player's likely next performance.
        <br /><br />
        <span style={{ color: '#2e9cca', fontSize: '1.1rem' }}>Give It A Try! </span> Start by searching for a players last name, and select your designated player to que the predictions. Search results will include the player's stats from their last 5 games, their next opponent, and what our program has predicted they might score. NOTE: if too close to game time, the program will use the next game to base its prediction off, keep an eye on the date.
        <br /><br />
        If you're using this for betting purposes, we recommend visiting our Odds Hub afterward to find the betting site offering the best value based on our predictor's suggestions. Additionally, we advise applying a 2-3 point buffer to the predicted number for greater flexibility.
        <br /><br />
        Best of luck!
        <br /><br />
        <span style={{ color: '#e63946', fontWeight: 'bold' }}>**DISCLAIMER** </span> All predictions are based solely on statistical data and trends. It's impossible to account for every variable that can influence professional sports outcomes. Please use this information responsibly.
    </p>
</div>

{/* SEARCH BAR */}
<div className='search-container'>
      <input
        className='search-input'
        type="text"
        placeholder="Enter player name"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
      />
      <button
        className='search-button' 
        onClick={() => {
            fetchPlayers()
            setResult()
        }}>
        Predict
        </button>
</div>

{/* Display player options */}
{players.length > 0 && (
    <div className="player-list">
        {players.map((player) => (
            <div 
                key={player.id} 
                className={`player-option ${selectedPlayer?.id === player.id ? 'selected' : ''}`}  
                onClick={() => handlePlayerSelect(player)}
            >
                {player.firstname} {player.lastname}
            </div>
        ))}
    </div>
)}



{/* LOADER */}
{loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: 4 }}>
            <Box className="loading-container">
            <CircularProgress
                sx={{
                color: 'rgba(88, 166, 255, 0.9)',
                animation: 'glow 1.5s infinite ease-in-out',
                }}
            />
            <span className="loading-text">Loading...</span>
            </Box>
        </Box>
    )}


{error && <p style={{ color: "red" }}>Can't find player. Make sure spelling is correct</p>}

{result && (
    <div>

<Box
      sx={{
        textAlign: 'center',
        marginBottom: '20px',
      }}>
      <h3
        style={{
          fontSize: '1.8rem',
          fontWeight: 'bold',
          color: '#f0f0f0',
          textShadow: '0px 4px 10px rgba(255, 255, 255, 0.2)',
          margin: 0,
        }}>
        {result.player_name}
      </h3>
    </Box>

<Box sx={{ display: 'flex', flexDirection: {xs: 'column', md: 'row'} , gap: '20px', margin: '40px'}}>

<Box sx={{ flex: {xs: 'none', md: 2}, width: {xs: '100%', md: 'auto'}, overflow: 'auto', marginLeft: {xs: '0px', md: '50px'} }}>

{/* TABLE  */}
<TableContainer
  component={Paper}
  sx={{
    height: {xs: 600, md: 600},
    width: {xs: '100%',sm: 450, md: 500},
    backgroundColor: '#1e1e2f', 
    boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.5)', 
    borderRadius: 3, 
    overflow: 'auto', 
  }}>
  <Table
    sx={{
      height: 600,
      width: 500,
      color: '#fff',
    }}
    aria-label="futuristic table"
  >
    <TableHead>
      <TableRow
        sx={{
          background: 'linear-gradient(90deg, #8e44ad, #3498db)', 
        }}>
        {['Matchup', 'Date', 'Win/Loss', 'REB', 'AST', 'PTS'].map((header) => (
          <TableCell
            key={header}
            align="right"
            sx={{
              color: '#fff', 
              fontWeight: 'bold',
              fontSize: '1.1rem',
              borderBottom: 'none', 
              textShadow: '0px 1px 4px rgba(255, 255, 255, 0.5)', 
            }}>
            {header}
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
    <TableBody>
      {rows.map((row, index) => (
        <TableRow
          key={row.name}
          sx={{
            backgroundColor: '#2a2a3c',
            '&:nth-of-type(even)': {
              backgroundColor: '#232332', 
            },
            '&:hover': {
              background:
                'linear-gradient(90deg, rgba(142,68,173,0.5), rgba(52,152,219,0.5))', 
              cursor: 'pointer',
              transform: 'scale(1.01)',
              transition: 'transform 0.2s ease, background 0.2s ease',
            },
          }}>
          <TableCell
            align="center"
            sx={{
              color: '#fff',
              fontSize: '0.9rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)', 
            }}>
            {row.matchup}
          </TableCell>
          <TableCell
            align="center"
            sx={{
              color: '#fff',
              fontSize: '0.9rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}>
            {row.date}
          </TableCell>
          <TableCell
            align="center"
            sx={{
              color: row.wl === 'W' ? 'green' : 'red', //
              fontWeight: 'bold',
              fontSize: '0.9rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}>
            {row.wl}
          </TableCell>
          <TableCell align="center" sx={{ color: '#fff' }}>
            {row.reb}
          </TableCell>
          <TableCell align="center" sx={{ color: '#fff' }}>
            {row.ast}
          </TableCell>
          <TableCell align="center" sx={{ color: '#fff' }}>
            {row.pts}
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>
</Box>

{/* INFO BOXES  */}
<Box
    sx={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      justifyContent: 'center',
      alignItems: {xs: 'center', md: 'flex-end'},
      textAlign: { xs: 'center', md: 'left' },
      marginRight: {xs: '0px', md: '50px'}
    }}>

    {/* Info Boxes */}
    <Box
      sx={{
        padding: '15px',
        backgroundColor: 'rgba(36, 36, 36, 0.95)',
        borderRadius: '15px',
        boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.3), 0px 4px 15px rgba(142, 68, 173, 0.5)',
        color: '#f0f0f0',
        fontSize: '1.2em',
        lineHeight: 1.5,
        border: '1px solid rgba(255, 255, 255, 0.2)',
        width: { xs: '90%', sm: '75%', md: '100%' },
        textAlign: 'center',
      }}
    >
      <p>Next Opponent: {getTeamName(result.next_opponent)} on {formatDate(result.next_opponent_date.slice(0,10))}</p>
    </Box>

    <Box
      sx={{
        padding: '15px',
        backgroundColor: 'rgba(36, 36, 36, 0.95)',
        borderRadius: '15px',
        boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.3), 0px 4px 15px rgba(52, 152, 219, 0.5)',
        color: '#f0f0f0',
        fontSize: '1.2rem',
        lineHeight: 1.5,
        border: '1px solid rgba(255, 255, 255, 0.2)',
        width: { xs: '90%', sm: '75%', md: '100%' },
        textAlign: 'center',
      }}
    >
      <p>{getTeamName(result.next_opponent)} allows {Math.round(result.opponent_allowed_ppg)} points per game</p>
    </Box>

    <Box
      sx={{
        padding: '15px',
        backgroundColor: 'rgba(36, 36, 36, 0.95)',
        borderRadius: '15px',
        boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.3), 0px 4px 15px rgba(142, 68, 173, 0.5)',
        color: '#f0f0f0',
        fontSize: '1.2rem',
        lineHeight: 1.5,
        border: '1px solid rgba(255, 255, 255, 0.2)',
        width: { xs: '90%', sm: '75%', md: '100%' },
        textAlign: 'center',
      }}
  >
    <p>{selectedPlayer.firstname} {selectedPlayer.lastname} averaged {averagePoints.toFixed(1)}pts in his last 5 games</p>
  </Box>

  <Box
    sx={{
      padding: '15px',
      backgroundColor: 'rgba(36, 36, 36, 0.95)',
      borderRadius: '15px',
      boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.3), 0px 4px 15px rgba(52, 152, 219, 0.5)',
      color: '#f0f0f0',
      fontSize: '1.2rem',
      lineHeight: 1.5,
      border: '1px solid rgba(255, 255, 255, 0.2)',
      width: { xs: '90%', sm: '75%', md: '100%' },
      textAlign: 'center',
    }}
  >
      <p>Predicted Points: {Math.round(result.predicted_points)}</p>
  </Box>

  </Box>
</Box>

</div>

         
  )
}
</div>
  );
}

export default PredictionModel;
