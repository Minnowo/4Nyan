-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 12, 2022 at 02:20 AM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 7.3.31

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `4nyan`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_file_info`
--

CREATE TABLE `tbl_file_info` (
  `hash_id` int(11) NOT NULL,
  `size` bigint(20) NOT NULL,
  `mime` int(11) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `duration` int(11) NOT NULL,
  `has_audio` tinyint(1) NOT NULL,
  `num_words` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_group`
--

CREATE TABLE `tbl_group` (
  `group_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `description` varchar(1024) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_group_map`
--

CREATE TABLE `tbl_group_map` (
  `group_id` int(11) NOT NULL,
  `hash_id` int(11) NOT NULL,
  `item_index` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_hash`
--

CREATE TABLE `tbl_hash` (
  `hash_id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tbl_hash`
--

INSERT INTO `tbl_hash` (`hash_id`, `hash`) VALUES
(2, 0x29bef8f333cc3720c15dde9653e9a08d59658b134962ea0fb74904058f4fc5fd);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_local_hashes`
--

CREATE TABLE `tbl_local_hashes` (
  `hash_id` int(11) NOT NULL,
  `md5` binary(16) NOT NULL,
  `sha1` binary(20) NOT NULL,
  `sha512` binary(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_namespace`
--

CREATE TABLE `tbl_namespace` (
  `namespace_id` int(11) NOT NULL,
  `namespace` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tbl_namespace`
--

INSERT INTO `tbl_namespace` (`namespace_id`, `namespace`) VALUES
(0, 'none'),
(1, 'none');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_rating`
--

CREATE TABLE `tbl_rating` (
  `rading_id` int(11) NOT NULL,
  `rating` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_subtag`
--

CREATE TABLE `tbl_subtag` (
  `subtag_id` int(11) NOT NULL,
  `subtag` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tbl_subtag`
--

INSERT INTO `tbl_subtag` (`subtag_id`, `subtag`) VALUES
(1, 'anime');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_tags`
--

CREATE TABLE `tbl_tags` (
  `tag_id` int(11) NOT NULL,
  `namespace_id` int(11) NOT NULL,
  `subtag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tbl_tags`
--

INSERT INTO `tbl_tags` (`tag_id`, `namespace_id`, `subtag_id`) VALUES
(7, 0, 1),
(11, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_tag_map`
--

CREATE TABLE `tbl_tag_map` (
  `hash_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_users`
--

CREATE TABLE `tbl_users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(32) NOT NULL,
  `hashed_password` varchar(80) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_admin` tinyint(1) NOT NULL,
  `disabled` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tbl_users`
--

INSERT INTO `tbl_users` (`user_id`, `username`, `hashed_password`, `created_at`, `is_admin`, `disabled`) VALUES
(1, 'test', 'here is my password hash uwu', '2022-04-12 00:01:57', 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_watched`
--

CREATE TABLE `tbl_watched` (
  `hash_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating_id` int(11) NOT NULL,
  `watch_time` int(11) NOT NULL,
  `watch_count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_file_info`
--
ALTER TABLE `tbl_file_info`
  ADD PRIMARY KEY (`hash_id`);

--
-- Indexes for table `tbl_group`
--
ALTER TABLE `tbl_group`
  ADD PRIMARY KEY (`group_id`);

--
-- Indexes for table `tbl_group_map`
--
ALTER TABLE `tbl_group_map`
  ADD PRIMARY KEY (`hash_id`,`group_id`);

--
-- Indexes for table `tbl_hash`
--
ALTER TABLE `tbl_hash`
  ADD PRIMARY KEY (`hash_id`);

--
-- Indexes for table `tbl_local_hashes`
--
ALTER TABLE `tbl_local_hashes`
  ADD PRIMARY KEY (`hash_id`);

--
-- Indexes for table `tbl_namespace`
--
ALTER TABLE `tbl_namespace`
  ADD PRIMARY KEY (`namespace_id`);

--
-- Indexes for table `tbl_rating`
--
ALTER TABLE `tbl_rating`
  ADD PRIMARY KEY (`rading_id`);

--
-- Indexes for table `tbl_subtag`
--
ALTER TABLE `tbl_subtag`
  ADD PRIMARY KEY (`subtag_id`);

--
-- Indexes for table `tbl_tags`
--
ALTER TABLE `tbl_tags`
  ADD PRIMARY KEY (`tag_id`,`subtag_id`,`namespace_id`) USING BTREE,
  ADD UNIQUE KEY `namespace_id` (`namespace_id`,`subtag_id`) USING BTREE;

--
-- Indexes for table `tbl_tag_map`
--
ALTER TABLE `tbl_tag_map`
  ADD PRIMARY KEY (`hash_id`,`tag_id`);

--
-- Indexes for table `tbl_users`
--
ALTER TABLE `tbl_users`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `tbl_watched`
--
ALTER TABLE `tbl_watched`
  ADD PRIMARY KEY (`hash_id`,`user_id`) USING BTREE,
  ADD KEY `rating_id` (`rating_id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_group`
--
ALTER TABLE `tbl_group`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_hash`
--
ALTER TABLE `tbl_hash`
  MODIFY `hash_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tbl_rating`
--
ALTER TABLE `tbl_rating`
  MODIFY `rading_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_subtag`
--
ALTER TABLE `tbl_subtag`
  MODIFY `subtag_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_tags`
--
ALTER TABLE `tbl_tags`
  MODIFY `tag_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `tbl_users`
--
ALTER TABLE `tbl_users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_file_info`
--
ALTER TABLE `tbl_file_info`
  ADD CONSTRAINT `tbl_file_info_ibfk_1` FOREIGN KEY (`hash_id`) REFERENCES `tbl_hash` (`hash_id`);

--
-- Constraints for table `tbl_group_map`
--
ALTER TABLE `tbl_group_map`
  ADD CONSTRAINT `tbl_group_map_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `tbl_group` (`group_id`),
  ADD CONSTRAINT `tbl_group_map_ibfk_2` FOREIGN KEY (`hash_id`) REFERENCES `tbl_hash` (`hash_id`);

--
-- Constraints for table `tbl_local_hashes`
--
ALTER TABLE `tbl_local_hashes`
  ADD CONSTRAINT `tbl_local_hashes_ibfk_1` FOREIGN KEY (`hash_id`) REFERENCES `tbl_hash` (`hash_id`);

--
-- Constraints for table `tbl_tags`
--
ALTER TABLE `tbl_tags`
  ADD CONSTRAINT `tbl_tags_ibfk_1` FOREIGN KEY (`namespace_id`) REFERENCES `tbl_namespace` (`namespace_id`),
  ADD CONSTRAINT `tbl_tags_ibfk_2` FOREIGN KEY (`subtag_id`) REFERENCES `tbl_subtag` (`subtag_id`);

--
-- Constraints for table `tbl_tag_map`
--
ALTER TABLE `tbl_tag_map`
  ADD CONSTRAINT `tbl_tag_map_ibfk_1` FOREIGN KEY (`hash_id`) REFERENCES `tbl_hash` (`hash_id`),
  ADD CONSTRAINT `tbl_tag_map_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tbl_tags` (`tag_id`);

--
-- Constraints for table `tbl_watched`
--
ALTER TABLE `tbl_watched`
  ADD CONSTRAINT `tbl_watched_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`user_id`),
  ADD CONSTRAINT `tbl_watched_ibfk_2` FOREIGN KEY (`hash_id`) REFERENCES `tbl_hash` (`hash_id`),
  ADD CONSTRAINT `tbl_watched_ibfk_3` FOREIGN KEY (`rating_id`) REFERENCES `tbl_rating` (`rading_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
