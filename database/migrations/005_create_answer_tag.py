#
# file: migrations/0005_create_answer.py
#
from yoyo import step

__depends__ = {"004_create_answer", "003_create_activity"}

steps = [ 
    step(
        "DROP TABLE IF EXISTS `mood`.`answer_tag`"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS `answer_tag` (
            `id_answer` INT NOT NULL,
            `id_activity` INT NOT NULL,
            PRIMARY KEY (`id_answer`, `id_activity`),
            INDEX `id_activity_FK_idx` (`id_activity` ASC) VISIBLE,
            CONSTRAINT `id_answer_FK`
            FOREIGN KEY (`id_answer`)
            REFERENCES `mood`.`answer` (`id_answer`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION,
            CONSTRAINT `id_activity_FK`
            FOREIGN KEY (`id_activity`)
            REFERENCES `mood`.`activity` (`id_activity`)
            ON DELETE NO ACTION
            ON UPDATE NO ACTION)
        ENGINE = InnoDB;
        """
    )
]
