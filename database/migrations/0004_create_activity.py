#
# file: migrations/0004_create_activity.py
#
from yoyo import step

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`activity`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `mood`.`activity` (
            `id_activity` INT NOT NULL,
            `activity_name` VARCHAR(50) NOT NULL,
            `activity_comment` VARCHAR(250) NULL,
            PRIMARY KEY (`id_activity`))
        ENGINE = InnoDB;
        """
    )
]
