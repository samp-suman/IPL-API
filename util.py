import pandas as pd
import numpy as np

matches = pd.read_csv('matches.csv')
balls = pd.read_csv('match+ball.csv')


def team1vsteam2(team, team2):

    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | (
        (matches['Team2'] == team) & (matches['Team1'] == team2))].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp-won-nr

    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr}


def allRecord(team):

    df = matches[(matches['Team1'] == team) | (
        matches['Team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp-won-nr
    nt = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]

    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr,
            'title': nt}


def teamAPI(team, matches=matches):

    df = matches[(matches['Team1'] == team) | (
        matches['Team2'] == team)].copy()
    self_record = allRecord(team)
    TEAMS = matches.Team1.unique()
    TEAMS = np.delete(TEAMS, np.argwhere(TEAMS == team))
    against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}

    return {team: {'all': self_record,
                   'against': against}}


def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = runs/out
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = runs/nballs * 100
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(
            ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score)+'*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates(
        'ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strikeRate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highestScore': highest_score,
        'notOut': not_out,
        'mom': mom
    }

    return data


def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsmanRecord(batsman, df)


def batsmanAPI(batsman, balls=balls):

    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = balls[balls['batsman']==batsman].BowlingTeam.unique()

    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'all': self_record,
                  'against': against}
    }
    return data


def bowlerRecord(bowler, df):
    if df.empty:
        return np.nan

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = runs/nballs*6
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = runs/wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs/wicket
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[
                                 False, True])[['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates(
        'ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'avg': avg,
        'strikeRate': strike_rate,
        'fours': fours,
        'sixes': sixes,
        'best_figure': best_figure,
        '3+W': w3,
        'mom': mom
    }

    return data


def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler, balls=balls):

    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = balls[balls['bowler']==bowler].BattingTeam.unique()

    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'all': self_record,
                 'against': against}
    }
    return data
