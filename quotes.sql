-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema belt_exam
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema belt_exam
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `belt_exam` ;
USE `belt_exam` ;

-- -----------------------------------------------------
-- Table `belt_exam`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `belt_exam`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(45) NULL,
  `last_name` VARCHAR(45) NULL,
  `email` VARCHAR(100) NULL,
  `password` VARCHAR(60) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `belt_exam`.`quotes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `belt_exam`.`quotes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quote` TEXT NULL,
  `author` VARCHAR(100) NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_quotes_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_quotes_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `belt_exam`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `belt_exam`.`users_has_quotes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `belt_exam`.`users_has_quotes` (
  `user_id` INT NOT NULL,
  `quote_id` INT NOT NULL,
  PRIMARY KEY (`user_id`, `quote_id`),
  INDEX `fk_users_has_quotes_quotes1_idx` (`quote_id` ASC) VISIBLE,
  INDEX `fk_users_has_quotes_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_quotes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `belt_exam`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_quotes_quotes1`
    FOREIGN KEY (`quote_id`)
    REFERENCES `belt_exam`.`quotes` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
