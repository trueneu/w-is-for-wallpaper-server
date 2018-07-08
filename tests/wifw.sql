-- MySQL dump 10.13  Distrib 5.6.31, for osx10.11 (x86_64)
--
-- Host: localhost    Database: wifw
-- ------------------------------------------------------
-- Server version	5.6.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `image_id_cover` bigint(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `image_id_cover_idx` (`image_id_cover`),
  CONSTRAINT `image_id_cover` FOREIGN KEY (`image_id_cover`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categories_to_images_mapping`
--

DROP TABLE IF EXISTS `categories_to_images_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories_to_images_mapping` (
  `category_id` int(11) NOT NULL,
  `image_id` bigint(10) NOT NULL,
  `mtime` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`category_id`,`image_id`),
  KEY `image_idx` (`image_id`),
  CONSTRAINT `category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image` FOREIGN KEY (`image_id`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categories_to_themes_mapping`
--

DROP TABLE IF EXISTS `categories_to_themes_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories_to_themes_mapping` (
  `category_id` int(11) NOT NULL,
  `theme_id` bigint(20) NOT NULL,
  PRIMARY KEY (`category_id`,`theme_id`),
  KEY `theme_idx` (`theme_id`),
  CONSTRAINT `theme` FOREIGN KEY (`theme_id`) REFERENCES `themes` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `colors`
--

DROP TABLE IF EXISTS `colors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `colors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `r` tinyint(3) unsigned DEFAULT '0',
  `g` tinyint(3) unsigned DEFAULT '0',
  `b` tinyint(3) unsigned DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `colors_to_images_mapping`
--

DROP TABLE IF EXISTS `colors_to_images_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `colors_to_images_mapping` (
  `color_id` int(11) NOT NULL,
  `image_id` bigint(11) NOT NULL,
  `mtime` datetime(6) DEFAULT NULL,
  `ordering` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`color_id`,`image_id`),
  KEY `image_id_idx` (`image_id`),
  CONSTRAINT `color_id` FOREIGN KEY (`color_id`) REFERENCES `colors` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_id` FOREIGN KEY (`image_id`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_type` int(11) NOT NULL,
  `entity_type` int(11) NOT NULL,
  `entity_id` bigint(20) NOT NULL,
  `date` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `image_coords_band`
--

DROP TABLE IF EXISTS `image_coords_band`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `image_coords_band` (
  `image_id` bigint(10) NOT NULL,
  `x0` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y0` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `x1` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y1` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `image_coords_cellphone`
--

DROP TABLE IF EXISTS `image_coords_cellphone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `image_coords_cellphone` (
  `image_id` bigint(10) NOT NULL,
  `x0` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y0` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `x1` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y1` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `image_coords_desktop`
--

DROP TABLE IF EXISTS `image_coords_desktop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `image_coords_desktop` (
  `image_id` bigint(10) NOT NULL,
  `x0` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y0` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `x1` int(11) DEFAULT NULL COMMENT 'upper left coord',
  `y1` int(11) DEFAULT NULL COMMENT 'bottom right coord',
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `images` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `thumbnail` text NOT NULL,
  `source` text NOT NULL,
  `license` int(11) NOT NULL,
  `uid` varchar(64) NOT NULL,
  `mtime` datetime(6) NOT NULL,
  `origin` text NOT NULL,
  `votes` int(11) DEFAULT '0',
  `rating_multiplier` float DEFAULT '1',
  `rating_addition` float DEFAULT '0',
  `rating` float DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_UNIQUE` (`uid`),
  KEY `license_idx` (`license`),
  KEY `mtime` (`mtime`),
  KEY `rating` (`rating`),
  CONSTRAINT `license` FOREIGN KEY (`license`) REFERENCES `licenses` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `images_daily`
--

DROP TABLE IF EXISTS `images_daily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `images_daily` (
  `category_id` int(11) NOT NULL,
  `type` smallint(6) NOT NULL,
  `image_id` bigint(20) DEFAULT NULL,
  `mtime` datetime DEFAULT NULL,
  KEY `category_type_mtime` (`category_id`,`type`,`mtime`),
  KEY `image_id_frgn_idx` (`image_id`),
  CONSTRAINT `category_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `licenses`
--

DROP TABLE IF EXISTS `licenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `licenses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) DEFAULT NULL,
  `url` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `themes`
--

DROP TABLE IF EXISTS `themes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `themes` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `image_id_desktop` bigint(20) DEFAULT NULL,
  `image_id_cellphone` bigint(20) DEFAULT NULL,
  `image_id_band` bigint(20) DEFAULT NULL,
  `is_promoted` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `image_desktop_idx` (`image_id_desktop`),
  KEY `image_coords_cellphone_idx` (`image_id_cellphone`),
  KEY `image_coords_band_idx` (`image_id_band`),
  CONSTRAINT `image_band` FOREIGN KEY (`image_id_band`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_cellphone` FOREIGN KEY (`image_id_cellphone`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_coords_band` FOREIGN KEY (`image_id_band`) REFERENCES `image_coords_band` (`image_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_coords_cellphone` FOREIGN KEY (`image_id_cellphone`) REFERENCES `image_coords_cellphone` (`image_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_coords_desktop` FOREIGN KEY (`image_id_desktop`) REFERENCES `image_coords_desktop` (`image_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `image_desktop` FOREIGN KEY (`image_id_desktop`) REFERENCES `images` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-14 21:59:33
