CREATE TABLE `ticket_pool` (
  `ticket_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `lottery_id` int(11) NOT NULL,
  `check_in_date` datetime NOT NULL,
  `number_of_guests` int(11) NOT NULL,
  `number_of_rooms_requested` int(11) NOT NULL,
  `purpose` enum('FAMILY','FRIENDS','OTHERS') NOT NULL,
  `is_room_sharable` tinyint(1) NOT NULL,
  `ticket_status` enum('IN_LOTTEY','CONFIRMING','CONFIRMED','CANCELED','LOST') NOT NULL,
  PRIMARY KEY (`ticket_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `lottery_id_idx` (`lottery_id`),
  CONSTRAINT `lottery_id` FOREIGN KEY (`lottery_id`) REFERENCES `lottery_pool` (`lottery_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
