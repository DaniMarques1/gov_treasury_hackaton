# Full Stack APP for Axie Gov Treasury Data Hackathon - Daniboo

## The Mission
The main goal of this hackathon is to make a Community Asset Dashboard MVP to visualize our treasury operations. This dashboard will be a beacon of transparency. The purpose of this dashboard is to remove the barriers of understanding about how the treasury finances operate.
Participants can choose to focus on one or both of the following tracks:

## Goals
Track 1: Treasury Inflows and Outflows
Create a comprehensive visualization of our treasury's inflows and outflows. This includes:

Inflows: Breeding fees, R&C minting fees, marketplace fees, ascension fees, minting fees, and evolution fees

Outflows: Hack recovery funds (demonstrating the link between ETH in the treasury and the bridge) and treasury fund distributions

Provide both daily and weekly views to capture trends.

----------------------------------------------------------
Track 2: ETH Accumulation Tracker
Develop a system to track and display ETH accumulation in the treasury since March 29, 2022. This will offer a clear picture of our growing digital assets over time.

For the most impact, we encourage participants to do both tracks and include interactive elements like plots and dashboards.

----------------------------------------------------------

### Backend

- Python scripts used to retrieve and treat data from the treasury addresses.

#### Technologies used in the Backend:

- Python
- Pandas
- MongoDB

### Frontend

 - An application in the app streamlit that reads data from JSON or from MongoDB collections, showing charts for data analysis and visualization.

#### technologies used in the Frontend:

- Python
- Streamlit
- HTML

----------------------------------------------------------

### How to Use

This app shows data tracked from the Axie Gov Treasury, utilizing charts for a visual analysis.

### How to use

1 - Copy the git repository:
```bash
git clone git@github.com:DaniMarques1/gov_treasury_hackaton.git
```

2 - Access the Frontend Streamlit Local folder:
```bash
cd gov_treasury_hackaton
cd frontend
cd streamlit
```

3 - Install the requirements:
```bash
pip install -r requirements.txt
```

4 - Get the server page running:
```bash
streamlit run Homepage.py
```

### Online app:

It is also possible to see the app MVP via the link.
(https://govhackaton.streamlit.app/)
