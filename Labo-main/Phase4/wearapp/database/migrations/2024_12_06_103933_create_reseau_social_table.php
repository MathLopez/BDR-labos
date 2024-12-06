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
        Schema::create('reseau_sociaux', function (Blueprint $table) {
            $table->id('pkRéseau');
            $table->enum('typeSocial', [
                'Facebook',
                'Instagram',
                'X',
                'TikTok',
                'Youtube',
                'Snapchat',
                'LinkedIn',
                'Pinterest',
                'Telegram',
                'Discord',
                'Reddit',
                'Threads',
                'Flickr'
            ]);
            $table->string('url', 255);
            $table->foreignId('fkBoutique')->constrained('boutiques');
            $table->timestamps();
        });
    }


    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('reseau_social');
    }
};
