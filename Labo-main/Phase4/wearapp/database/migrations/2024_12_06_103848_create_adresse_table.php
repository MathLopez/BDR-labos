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
        Schema::table('adresses', function (Blueprint $table) {
            $table->dropForeign(['fkPays']); // Suppression de la contrainte de clé étrangère
        });

        Schema::dropIfExists('pays');  // Puis suppression de la table "pays"
    }

    public function down()
    {
        // Recréer la table pays et la contrainte si vous refaites une migration inverse
        Schema::create('pays', function (Blueprint $table) {
            $table->id('pkPays');
            $table->string('nom', 100);
            $table->decimal('fraisLivraison', 10, 2);
            $table->timestamps();
        });

        Schema::table('adresses', function (Blueprint $table) {
            // Ajouter à nouveau la contrainte de clé étrangère après avoir recréé la table pays
            $table->foreign('fkPays')->references('pkPays')->on('pays')->onDelete('cascade');
        });
    }
};
