CREATE DATABASE IF NOT EXISTS publication_listings;

USE publication_listings;

CREATE TABLE IF NOT EXISTS `Publication` (
  `Pub_ID` INT NOT NULL,
  `Title` VARCHAR(100) NULL,
  `DatePublished` DATE NULL,
  `Pages` VARCHAR(50) NULL,
  `DOI` VARCHAR(45) NULL,
  `Link` VARCHAR(200) NULL,
  `created_date` DATE NULL,
  `updated_date` DATE NULL,
  PRIMARY KEY (`Pub_ID`)
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Author` (
  `author_ID` INT NOT NULL,
  `FirstName` VARCHAR(45) NOT NULL,
  `LastName` VARCHAR(45) NULL,
  `Institution` VARCHAR(45) NULL,
  `Department` VARCHAR(45) NULL,
  `Email` VARCHAR(45) NULL,
  `Address` VARCHAR(45) NULL,
  `Homepage` VARCHAR(200) NULL,
  `Publication_id` INT NOT NULL,
  `created_date` DATE NULL,
  `updated_date` DATE NULL,
  PRIMARY KEY (`author_ID`, `Publication_idPublication`),
  INDEX `fk_Author_Publication_idx` (`Publication_idPublication` ASC) VISIBLE,
  CONSTRAINT `fk_Author_Publication`
    FOREIGN KEY (`Publication_idPublication`)
    REFERENCES `Publication` (`Pub_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Users` (
  `User_ID` INT NOT NULL,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Address` VARCHAR(200) NULL,
  `Email` VARCHAR(200) NULL,
  `created_date` DATE NULL,
  `updated_date` DATE NULL,
  PRIMARY KEY (`User_ID`)
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `Keywords` (
  `KeywordID` INT NULL,
  `Keyword` VARCHAR(45) NULL,
  `Publication_Pub_ID` INT NOT NULL,
  PRIMARY KEY (`Publication_Pub_ID`),
  CONSTRAINT `fk_Keywords_Publication1`
    FOREIGN KEY (`Publication_Pub_ID`)
    REFERENCES `Publication` (`Pub_ID`)
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

