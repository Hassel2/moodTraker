#
# file: migrations/0002_create_notification.py
#
from yoyo import step

__depends__ = {"001_create_chat"}

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`notification`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `mood`.`notification` (
            `id_chat` INT NOT NULL,
            `time` TIME NOT NULL,
            PRIMARY KEY (`id_chat`, `time`),
            CONSTRAINT `id_chat_FK`
            FOREIGN KEY (`id_chat`)
            REFERENCES `mood`.`chat` (`id_chat`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
        """
    )
]
