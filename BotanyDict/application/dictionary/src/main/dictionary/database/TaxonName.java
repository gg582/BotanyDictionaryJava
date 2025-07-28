package com.botany.dictionary.database;
import jakarta.persistence.Column;

public class TaxonName {
    @Column(unique = true) Integer id;
    @Column(unique = true) String name;
}