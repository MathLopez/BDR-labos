<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up()
    {
        DB::unprepared('
        CREATE OR REPLACE FUNCTION validate_avis()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM commandes c
                JOIN contient ct ON c.pkCommande = ct.fkCommande
                WHERE c.fkUtilisateur = NEW.fkUtilisateur
                  AND ct.fkArticleProduit = NEW.fkProduit
                  AND c.etat IN (\'commandé\', \'livré\')
            ) THEN
                RAISE EXCEPTION \'Utilisateur % n\'a pas commandé ou reçu le produit %\', NEW.fkUtilisateur, NEW.fkProduit;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    ');

        DB::unprepared('
        CREATE TRIGGER trigger_validate_avis
        BEFORE INSERT ON avis
        FOR EACH ROW
        EXECUTE FUNCTION validate_avis();
    ');
    }

    public function down()
    {
        DB::unprepared('DROP TRIGGER IF EXISTS trigger_validate_avis ON avis');
        DB::unprepared('DROP FUNCTION IF EXISTS validate_avis');
    }



};
