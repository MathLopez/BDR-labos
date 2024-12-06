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
        Schema::create('contient', function (Blueprint $table) {
            $table->foreignId('fkCommande')->constrained('commandes');
            $table->foreignId('fkArticleProduit')->constrained('articles', 'pkProduit');
            $table->string('fkArticleTaille', 10);
            $table->integer('quantité');
            $table->primary(['fkCommande', 'fkArticleProduit', 'fkArticleTaille']);
            $table->foreign(['fkArticleProduit', 'fkArticleTaille'])->references(['pkProduit', 'taille'])->on('articles');
            $table->timestamps();
        });
    }


    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('contient');
    }
};
