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
        Schema::create('avis', function (Blueprint $table) {
            $table->foreignId('fkProduit')->constrained('produits');
            $table->foreignId('fkUtilisateur')->constrained('utilisateurs');
            $table->decimal('note', 2, 1)->check('note IN (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)');
            $table->text('commentaire')->nullable();
            $table->primary(['fkProduit', 'fkUtilisateur']);
            $table->timestamps();
        });
    }


    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('avis');
    }
};
