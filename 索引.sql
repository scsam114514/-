create index CONCERN_MANUFACTURER_ID
  on concern (MANUFACTURER_ID);

create index EVALUATETABLE_GAME_ID
  on evaluatetable (GAME_ID);

create index EVALUATETABLE_USER_ID
  on evaluatetable (USER_ID);

create index FRIEND_USER_ID
  on friend (USER_ID);

create index GAME_MANUFACTURER_ID
  on game (MANUFACTURER_ID);

create index TYPE_GAME_ID
  on game_to_type (GAME_ID);

create index HAVING_GAMES_GAME_ID
  on having_games (GAME_ID);

create index DETAILS_GAME_ID
  on order_details (GAME_ID);
create index ORDER_USER_ID
  on order_for_goods (USER_ID);
  
CREATE INDEX idx_game_name ON game (GAME_NAME);