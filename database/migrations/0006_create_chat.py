#
# file: migrations/0001_create_chat.py
#
from yoyo import step

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`chat`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `mood`.`chat` (
            `id_chat` INT NOT NULL,
            `status` ENUM('active', 'inactive') NULL,
            `gender` ENUM('male', 'female') NULL,
            `age` INT(4) UNSIGNED NULL,
            PRIMARY KEY (`id_chat`))
        ENGINE = InnoDB;
        """
    )
]
