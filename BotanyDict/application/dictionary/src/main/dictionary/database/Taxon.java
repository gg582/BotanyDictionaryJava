package com.botany.dictionary.database;
import jakarta.persistence.Id;

public class Taxon {
    @Id private Integer id;
    private Integer parent_id;
    private String  rank;
    private Integer division_id; 
}

