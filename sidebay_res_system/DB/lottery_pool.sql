CREATE TABLE `lottery_pool` (
  `lottery_id` int(11) NOT NULL AUTO_INCREMENT,
  `lottery_start_day` datetime NOT NULL,
  `lottery_end_day` datetime NOT NULL,
  `check_in_start_day` datetime NOT NULL,
  `check_in_end_day` datetime NOT NULL,
  `expire_day` datetime NOT NULL,
  PRIMARY KEY (`lottery_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
