import settings
import pandas as pd
import mysql.connector
conn = mysql.connector.connect(
    host=settings.MYSQL_HOST,
    user=settings.MYSQL_USER,
    passwd=settings.MYSQL_PASSWORD,
    database=settings.MYSQL_NAME,
    #ssl_disabled = True
)
cur = conn.cursor(buffered=True)

def create_in_numbers(ids):
    in_numbers = ', '.join(list(map(lambda x: '%s', ids)))
    if in_numbers== "":
        in_numbers = 99999999
    return in_numbers

def get_all_from_series_player(min_date):
    sql = """
    select sp.series_id,player_id,sp.team_id,team_id_opponent, s.start_date_time
     from series_player sp
    join series s on s.id = sp.series_id
    join series_team st on st.series_id = sp.series_id and sp.team_id = st.team_id
    where s.start_date_time > %s
    """
    return pd.read_sql(sql,conn,params=[min_date])


def get_all_time_game_player_data(min_date):
    sql="""    
    select p.country,gp.player_id, gp.kills,gp.headshots,gp.deaths,gp.opening_kills,opening_deaths, gp.awp,t.name as tournament_name, is_offline,prize_pool,
    p.name as player_name, g.start_date_time,gt.rounds_won,gt.rounds_lost,gp.game_id,g.series_id,gt.team_id,map,g.game_number,adr,gt.won
    from game_player gp 
    join game g on g.id=gp.game_id
    join game_team gt on gt.game_id = gp.game_id and gp.team_id = gt.team_id
    join player p on p.id = gp.player_id  
    join series s on s.id=g.series_id
    join tournament t on s.tournament_id= t.id
    where g.start_date_time > %s
    """
    return pd.read_sql(sql,conn,params=[min_date])

def get_player():
    sql = """
    select p.id as player_id,p.name as player_name,p.country,region from player as p
    join country_region cr on cr.country = p.country
    """
    return pd.read_sql(sql,conn)

def  get_all_game_all_player_from_series_ids(series_ids):
    in_p = create_in_numbers(series_ids)
    sql = """
     select p.country,gp.player_id, gp.kills,gp.headshots,gp.deaths,gp.opening_kills,opening_deaths, gp.awp,t.name as tournament_name, is_offline,prize_pool,
    p.name as player_name, g.start_date_time,gt.rounds_won,gt.rounds_lost,gp.game_id,g.series_id,gt.team_id,map,g.game_number,adr,gt.won
    from game_player gp 
    join game g on g.id=gp.game_id
    join game_team gt on gt.game_id = gp.game_id and gp.team_id = gt.team_id
    join player p on p.id = gp.player_id  
    join series s on s.id=g.series_id
    join tournament t on s.tournament_id= t.id
    where s.id in (%s)
    order by g.start_date_time asc

    """
    sql = sql % in_p
    return pd.read_sql(sql, conn, params=series_ids)

def get_team():
    sql = """
    select t.id as team_id,t.name as team_name from team t
    """
    return pd.read_sql(sql,conn)

def get_all_series_ids(min_date):
    sql = """
    select id as series_id from series s
     where s.start_date_time >= %s 
    """
    return pd.read_sql(sql,conn,params=[min_date])

def get_all_game_ids(min_date):
    sql = """
    select id as game_id from game g
     where g.start_date_time > %s 
    """
    return pd.read_sql(sql,conn,params=[min_date])

def get_game_team_rating(min_date):
    sql = """
    select te.name as team_name,gt.team_id,rounds_won,gt.rounds_lost,map,gtr.rating,gtr.rating_opponent,won
    from game_team gt
    join team te on te.id = gt.team_id
    join game_team_rating gtr on gtr.game_id = gt.game_id and gtr.team_id = gt.team_id
    join game g on g.id = gt.game_id
    where g.start_date_time > %s and rounds_won+rounds_lost <> 30
    
    """
    return pd.read_sql(sql,conn,params=[min_date])


def get_game_team(min_date):
    sql = """
    select te.name as team_name,gt.team_id,rounds_won,gt.rounds_lost,map,won,start_date_time,game_number,game_id,gt.kills,gt.kills_opponent
    from game_team gt
    join team te on te.id = gt.team_id
    join game g on g.id = gt.game_id
    where g.start_date_time > %s and rounds_won+rounds_lost <> 30

    """
    return pd.read_sql(sql, conn, params=[min_date])
