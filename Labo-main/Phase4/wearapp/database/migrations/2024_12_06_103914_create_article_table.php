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
    Schema::create('articles', function (Blueprint $table) {
        $table->foreignId('pkProduit')->constrained('produits', 'pkProduit'); // Changement ici
        $table->string('taille', 10);
        $table->integer('quantiteDisponible');
        $table->primary(['pkProduit', 'taille']);  

        $table->timestamps();
    });
}



    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('article');
    }
};
