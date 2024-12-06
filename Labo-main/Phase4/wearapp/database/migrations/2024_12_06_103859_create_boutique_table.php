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
        Schema::create('boutiques', function (Blueprint $table) {
            $table->id('pkBoutique');
            $table->string('nom', 100);
            $table->string('urlOrigine', 255)->nullable();

            // Clé étrangère fkUtilisateur faisant référence à pkUtilisateur
            $table->foreignId('fkUtilisateur')->constrained('utilisateurs', 'pkUtilisateur');  // Changement ici

            $table->timestamps();
        });
    }



    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('boutique');
    }
};
