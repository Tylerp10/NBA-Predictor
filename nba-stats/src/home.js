import React from "react";
import { Box, Card, CardActionArea, CardMedia, CardContent, Typography } from "@mui/material";
import nbaLogo from './images/nba_logo.jpg'
import predictorPic from './images/nba-betting-tips.jpg'
import oddsPic from './images/nba-betting.jpg'

const cardStyle = {
    borderRadius: '15px', 
    boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.5)', 
    transition: 'transform 0.3s ease, box-shadow 0.3s ease', 
    '&:hover': {
      transform: 'translateY(-10px)',
      boxShadow: '0px 15px 25px rgba(0, 0, 0, 0.2)', 
    },
  };
    

function Home(){
    return (
        
        <div className="background">

        <Box
            sx={{
                height: '120px', 
                width: '100%',
                bgcolor: 'rgba(48, 48, 60, 0.95)', 
                borderRadius: 5,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 10px 20px rgba(0, 0, 0, 0.5)', 
                position: 'relative',
            }}>

            <Box
                sx={{
                    textAlign: 'center',
                    color: '#ffffff',
                    fontSize: { xs: '2rem', sm: '3rem', md: '4rem' }, 
                    fontWeight: 'bold',
                    letterSpacing: '0.75rem',
                    textShadow: '0 2px 4px rgba(255, 223, 0, 0.5), 0 4px 10px rgba(255, 153, 0, 0.7)',
                    userSelect: 'none',
                }}>
                Hoop Scope
            </Box>
        </Box>


        <div className="welcome-container">
            <h4 className="welcome-title">Welcome to Hoop Scope!</h4>
            <p className="welcome-message">Are you passionate about numbers, an NBA fanatic, and someone who enjoys placing the occasional sports bet? Then HoopScope is the perfect place for you! Our platform is packed with everything you need, from player averages and recent performances to betting odds and more. Want to see how your favorite player is performing this season? Visit the Players Hub for up-to-date season averages. Looking for the best value on your bets? Check out the Odds Hub to find top betting sites. Curious about what our model predicts for your player's next game? Head over to the Point Predictor for an estimate. With all these tools at your fingertips, HoopScope is your ultimate resource for making smarter, winning NBA bets!</p>
        </div>

<Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, flexWrap: 'wrap', marginTop: '50px' }}>
  <Box sx={{ maxWidth: 345, height: '450px' }}>
    <Card sx={cardStyle}>
      <CardActionArea href="/players">
        <CardMedia
          component="img"
          height="300"
          image={nbaLogo}
          alt="Players Hub"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Players Hub
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Explore every NBA roster and dive deep into player averages for the current season. 
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  </Box>

  <Box sx={{ maxWidth: 345, height: '450px' }}>
    <Card sx={cardStyle}>
      <CardActionArea href="/predictor">
        <CardMedia
          component="img"
          height="300"
          image={predictorPic}
          alt="Points Predictor"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Points Predictor
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Review your favorite players' recent performances and receive a statistically-driven point prediction for their upcoming game.
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  </Box>

  <Box sx={{ maxWidth: 345, height: '450px' }}>
    <Card sx={cardStyle}>
      <CardActionArea href="/odds">
        <CardMedia
          component="img"
          height="300"
          image={oddsPic}
          alt="Odds Hub"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Odds Hub
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Explore a wide range of betting options across multiple sites to ensure you're getting the best value for your bet.
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  </Box>
</Box>




        </div>
    )
}

export default Home