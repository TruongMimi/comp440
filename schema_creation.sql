CREATE DATABASE IF NOT EXISTS publication_listings;

USE publication_listings;

CREATE TABLE IF NOT EXISTS `Publication` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Title` VARCHAR(200) NULL,
  `DatePublished` DATE NULL,
  `Pages` VARCHAR(200) NULL,
  `DOI` VARCHAR(200) NULL,
  `Link` VARCHAR(200) NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Author` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(200) NOT NULL,
  `LastName` VARCHAR(200) NULL,
  `Institution` VARCHAR(200) NULL,
  `Department` VARCHAR(200) NULL,
  `Email` VARCHAR(200) NULL,
  `Address` VARCHAR(200) NULL,
  `Homepage` VARCHAR(200) NULL,
  `Publication_id` INT NOT NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  INDEX `fk_Author_Publication_idx` (`Publication_id` ASC),
  CONSTRAINT `fk_Author_Publication`
    FOREIGN KEY (`Publication_id`)
    REFERENCES `Publication` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Users` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(200) NULL,
  `LastName` VARCHAR(200) NULL,
  `Address` VARCHAR(200) NULL,
  `Email` VARCHAR(200) NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Keywords` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Keyword` VARCHAR(200) NULL,
  `Publication_Pub_ID` INT NOT NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  CONSTRAINT `fk_Keywords_Publication1`
    FOREIGN KEY (`Publication_Pub_ID`)
    REFERENCES `Publication` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB;

-- Create a new user 'newuser' with appropriate hostname settings
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password' REQUIRE NONE;

-- Grant privileges to newuser on publication_listings database
GRANT ALL PRIVILEGES ON publication_listings.* TO 'newuser'@'localhost';

-- Alter newuser to use mysql_native_password authentication plugin
-- if needed: ALTER USER 'newuser'@'localhost' IDENTIFIED BY 'password' REQUIRE NONE;
