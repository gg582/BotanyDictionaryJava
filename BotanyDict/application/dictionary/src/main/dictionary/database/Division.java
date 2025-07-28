package com.botany.dictionary.database;
import jakarta.persistence.Id;

public class Division {

    @Id private Integer id;
    private String code;
    private String name;
    private String comments;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return code;
    }

    public void setName() {
        this.code = code;
    }

    public String getComments() {
        return comments;
    }

    public void setComments() {
        this.comments = comments;
    }
}
