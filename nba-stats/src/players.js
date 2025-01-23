import './App.css';
import React, { useEffect, useState } from 'react';
import { Box } from '@mui/material';
import { Link } from 'react-router-dom';

function Players() {

  const [teams, setTeams] = useState([])
  const [selectedTeam, setSelectedTeam] = useState()
  const [roster, setRoster] = useState([])
  const [selectedPlayer, setSelectedPlayer] = useState()
  const [stats, setStats] = useState([])

  useEffect(() => {

    async function fetchTeams() {
      const response = await fetch("https://nba-predictor-9f7k.onrender.com/teams")
      const data = await response.json()
      // console.log(data)
      setTeams(Object.entries(data).map(([name, id]) => ({ name, id })))
    }    
    fetchTeams()
  }, [])

  async function fetchRoster(teamId) {
    const response = await fetch(`https://nba-predictor-9f7k.onrender.com/rosters?team_id=${teamId}`)
    const data = await response.json()
    setRoster(Object.entries(data).map(([name, id]) => ({name, id})))
  }

  async function fetchStats(playerId) {
    const response = await fetch(`https://nba-predictor-9f7k.onrender.com/averages?player_id=${playerId}`)
    const data = await response.json()
    const filteredStats = [
      {name: "Points", value: data.points},
      {name: "Assists", value: data.assists},
      {name: "Rebounds", value: data.rebounds},
      {name: "Steals", value: data.steals},
      {name: "Blocks", value: data.blocks},
      {name: "Field Goals Made", value: data.field_goals_made},
      {name: "Field Goals Attempted", value: data.field_goals_att},
      {name: "Three Pointers Made", value: data.three_points_made},
      {name: "Three Pointers Attempted", value: data.three_points_att},
    ];
    setStats(filteredStats)
  }


  return (
    <div className='background'>

{/* NAVBAR */}
<Box 
    sx={{
        width: '100%',
        bgcolor: 'rgba(48, 48, 60, 0.95)', 
        borderRadius: '10px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.25)', 
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
        <h2 
            style={{
                margin: 0,
                fontSize: { xs: '1.5rem', sm: '2rem' },
                color: '#f4f4f4',
                fontWeight: 'bold',
                textShadow: '0 4px 10px rgba(255, 255, 255, 0.5)',
            }}>
            Players
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
<Box 
  sx={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
  }}
>
  {/* Team Selection */}
  <Box
    sx={{
      display: 'flex',
      flexWrap: 'wrap',
      justifyContent: 'center',
      gap: '15px',
      width: '80%',
      marginBottom: '30px',
    }}
  >
    {teams.map((team) => (
      <button 
        key={team.id} 
        onClick={() => {
          setSelectedTeam(team);
          fetchRoster(team.id);
          setSelectedPlayer(null);
        }}
        className="team-button"
      >
        {team.name}
      </button>
    ))}
  </Box>

  {/* Roster Display */}
  {selectedTeam && (
    <Box 
      sx={{
        backgroundColor: 'rgba(48, 48, 60, 0.95)',
        padding: '20px',
        borderRadius: '25px',
        boxShadow: '0px 10px 30px rgba(0, 0, 0, 1)',
        width: '100%',
        maxWidth: '900px',
        marginBottom: '20px',
      }}
    >
      <h3 style={{ color: '#58a6ff', textAlign: 'center', marginBottom: '20px', fontSize: '1.5rem', fontWeight: 400, letterSpacing: 1.5 }}>
        {selectedTeam.name}
      </h3>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '10px',
        }}
      >
        {roster.map((player) => (
          <button 
            key={player.id} 
            onClick={() => {
              setSelectedPlayer(player);
              fetchStats(player.id);
            }}
            className="player-button"
          >
            {player.name}
          </button>
        ))}
      </Box>
    </Box>
  )}

  {/* Player Stats Display */}
  {selectedPlayer && (
    <Box 
      sx={{
        backgroundColor: 'rgba(36, 36, 36, 0.95)',
        padding: '20px',
        borderRadius: '20px',
        boxShadow: '0px 10px 30px rgba(0, 0, 0, 0.5)',
        width: '100%',
        maxWidth: '600px',
        textAlign: 'center',
      }}
    >
      <h3 style={{ color: '#58a6ff', marginBottom: '20px', fontSize: '1.25rem' }}>
        {selectedPlayer.name}
      </h3>
      <h5 style={{ color: '#f0f0f0', marginBottom: '10px', fontSize: '1rem' }}>Season Averages:</h5>
      <ul 
        style={{ 
          listStyleType: 'none', 
          padding: 0, 
          color: '#f0f0f0', 
          lineHeight: '1.8',
        }}
      >
        {stats.map((stat) => (
          <li key={stat.name}>
            {stat.name}: <strong>{stat.value}</strong>
          </li>
        ))}
      </ul>
    </Box>
  )}
</Box>

      

    </div>
  )
}

export default Players;
