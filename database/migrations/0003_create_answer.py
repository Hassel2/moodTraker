#
# file: migrations/0003_create_answer.py
#
from yoyo import step

__depends__ = {"0006_create_chat"}

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`answer`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `mood`.`answer` (
            `id_answer` INT NOT NULL,
            `id_chat` INT NOT NULL,
            `answer_time` DATETIME NOT NULL,
            `rating` INT(2) UNSIGNED NOT NULL,
            `answer_comment` VARCHAR(500) NULL,
            `media_path` VARCHAR(500) NULL,
            `answercol` VARCHAR(45) NULL,
            PRIMARY KEY (`id_answer`),
            INDEX `user_id_FK_idx` (`id_chat` ASC) VISIBLE,
            CONSTRAINT `id_chat_FK`
            FOREIGN KEY (`id_chat`)
            REFERENCES `mood`.`chat` (`id_chat`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
        """
    )
]
