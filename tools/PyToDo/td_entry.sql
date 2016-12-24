
DROP TABLE IF EXISTS `td_entry`;
CREATE TABLE `td_entry` (
  `entry_id` int(11) NOT NULL AUTO_INCREMENT,
  `entry_content` varchar(1024) NOT NULL DEFAULT '' COMMENT '内容',
  `entry_type` int(11) NOT NULL DEFAULT '0',
  `entry_status` tinyint(4) NOT NULL DEFAULT '0',
  `begin_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `status` int(11) NOT NULL DEFAULT '1',
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  PRIMARY KEY (`entry_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
