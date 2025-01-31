"""add products_summary to projects

Revision ID: 54ce9cc70ef7
Revises: c85794cd9982
Create Date: 2024-01-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '54ce9cc70ef7'
down_revision = 'c85794cd9982'  # Points to the initial migration
branch_labels = None
depends_on = None


def upgrade():
    # Add products_summary column
    op.add_column('projects', sa.Column('products_summary', 
        postgresql.JSONB, 
        nullable=False, 
        server_default='{"products": [], "total_count": 0}'
    ))

    # Create trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_project_products_summary()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                -- Add new product to summary
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (products_summary->'products') || 
                        jsonb_build_object(
                            'id', NEW.id::text, 
                            'name', NEW.name,
                            'description', NEW.description
                        )::jsonb
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int + 1)::text::jsonb
                )
                WHERE id = NEW.project_id;
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                -- Update product name and description in summary if they changed
                IF OLD.name <> NEW.name OR OLD.description IS DISTINCT FROM NEW.description THEN
                    UPDATE projects 
                    SET products_summary = jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(
                                CASE 
                                    WHEN (value->>'id')::uuid = NEW.id 
                                    THEN jsonb_build_object(
                                        'id', NEW.id::text, 
                                        'name', NEW.name,
                                        'description', NEW.description
                                    )
                                    ELSE value 
                                END
                            )
                            FROM jsonb_array_elements(products_summary->'products')
                        )
                    )
                    WHERE id = NEW.project_id;
                END IF;
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                -- Remove product from summary
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(value)
                            FROM jsonb_array_elements(products_summary->'products')
                            WHERE (value->>'id')::uuid <> OLD.id
                        )
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int - 1)::text::jsonb
                )
                WHERE id = OLD.project_id;
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
        CREATE TRIGGER product_changes
        AFTER INSERT OR UPDATE OR DELETE ON products
        FOR EACH ROW EXECUTE FUNCTION update_project_products_summary();
    """)

    # Create utility function to rebuild summary
    op.execute("""
        CREATE OR REPLACE FUNCTION rebuild_project_products_summary(project_uuid uuid)
        RETURNS void AS $$
        BEGIN
            UPDATE projects
            SET products_summary = (
                SELECT jsonb_build_object(
                    'products', COALESCE(jsonb_agg(
                        jsonb_build_object(
                            'id', id::text, 
                            'name', name,
                            'description', description
                        )
                    ), '[]'::jsonb),
                    'total_count', COUNT(*)
                )
                FROM products
                WHERE project_id = project_uuid
            )
            WHERE id = project_uuid;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Initialize products_summary for existing projects
    op.execute("""
        SELECT rebuild_project_products_summary(id) FROM projects;
    """)


def downgrade():
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS product_changes ON products;")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_project_products_summary();")
    op.execute("DROP FUNCTION IF EXISTS rebuild_project_products_summary(uuid);")
    
    # Drop column
    op.drop_column('projects', 'products_summary')
