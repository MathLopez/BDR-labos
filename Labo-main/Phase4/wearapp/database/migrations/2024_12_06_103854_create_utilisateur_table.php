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
        Schema::create('utilisateurs', function (Blueprint $table) {
            $table->id('pkUtilisateur');  // Cette colonne doit être définie comme clé primaire
            $table->enum('role', ['Client', 'Vendeur', 'Admin']);
            $table->string('nom', 100);
            $table->string('prenom', 100);
            $table->string('email', 150)->unique();
            $table->date('dateNaissance');
            $table->string('motDePasse');
            $table->foreignId('fkAdresseLivraison')->constrained('adresses', 'pkAdresse');
            $table->foreignId('fkAdresseFacturation')->constrained('adresses', 'pkAdresse');
            $table->timestamps();
        });
    }




    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('utilisateur');
    }
};
