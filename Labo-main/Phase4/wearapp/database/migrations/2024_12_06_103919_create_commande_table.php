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
        Schema::create('commandes', function (Blueprint $table) {
            $table->id('pkCommande');
            $table->timestamp('date')->default(DB::raw('CURRENT_TIMESTAMP'));
            $table->decimal('prix', 10, 2);
            $table->enum('typePaiement', ['twint', 'paypal', 'cb']);
            $table->enum('état', ['panier', 'commandé', 'livré']);

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
        Schema::dropIfExists('commande');
    }
};
