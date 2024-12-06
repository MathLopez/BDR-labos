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
        Schema::create('produits', function (Blueprint $table) {
            $table->id('pkProduit');  // Cette colonne doit être définie comme clé primaire
            $table->string('nom', 100);
            $table->text('description')->nullable();
            $table->date('dateAjout')->default(DB::raw('CURRENT_DATE'));
            $table->decimal('prix', 10, 2);
            $table->enum('sexe', ['Homme', 'Femme', 'Unisexe'])->nullable();
            $table->foreignId('fkCategorie')->constrained('categories', 'pkCategorie');
            $table->foreignId('fkBoutique')->constrained('boutiques', 'pkBoutique');
            $table->timestamps();
        });
    }




    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('produit');
    }
};
