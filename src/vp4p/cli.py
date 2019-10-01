# -*- coding: utf-8 -*-

"""Command line interface."""

import logging

import click
import pandas as pd

from vp4p.sample_scoring import (
    do_limma, do_z_score, do_ssgsea
)
from vp4p.embedding import (
    do_row2vec, do_path2vec, do_thresh2vec, do_nrl
)

logger = logging.getLogger(__name__)


@click.group(help='vp4p')
def main():
    """Run vp4p."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


@main.group()
def sample_scoring():
    """
        List Single Sample Scoring methods available.
    """

data_option = click.option(
    '--data',
    help="Path to tab-separated gene expression data file",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    required=True
)

design_option = click.option(
    '--design',
    help="Path to tab-separated experiment design file",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    required=True
)
output_option = click.option(
    '--out',
    help="Path to the output file",
    type=click.Path(file_okay=True, dir_okay=False, exists=False),
    required=True
)
control_option = click.option(
    '--control',
    help="Annotated value for the control samples (Must start with an alphabet)",
    type=str,
    required=False,
    default='Control',
    show_default=True
)


@sample_scoring.command(help='Limma based Single Sample Scoring')
@data_option
@design_option
@output_option
@click.option(
    '--alpha',
    help="Family-wise error rate",
    type=float,
    required=False,
    default=0.05,
    show_default=True
)
@click.option(
    '--method',
    help="Method used for testing and adjustment of P-Values",
    type=str,
    required=False,
    default='fdr_bh',
    show_default=True
)
@control_option
def limma(data, design, out, alpha, method, control) -> None:
    click.echo(f"Starting Limma Based Single Sample Scoring with {data} & {design} files and saving it to {out}")

    data_df = pd.read_csv(data, sep='\t', index_col=0)
    design_df = pd.read_csv(design, sep='\t')

    ctrl_data = data_df.transpose()[list(design_df.Target == control)].transpose()
    sample_data = data_df.transpose()[list(design_df.Target != control)].transpose()

    ctrl_design = design_df[list(design_df.Target == control)]
    sample_design = design_df[list(design_df.Target != control)]

    output_df = pd.DataFrame(columns=sample_data.index, index=sample_data.columns)

    for col_idx, col in enumerate(sample_data.columns):
        data_df = ctrl_data.copy()

        data_df[col] = sample_data.iloc[:, col_idx]
        design_df = ctrl_design.append(sample_design.iloc[col_idx, :], ignore_index=True)

        output = do_limma(data=data_df, design=design_df, alpha=alpha, adjust_method=method)
        output_df.iloc[col_idx, :] = output['logFC'].values.flatten()

    output_df.to_csv(out, sep='\t')

    click.echo(f"Done With limma calculation for {data}")


@sample_scoring.command(help='Z-Score based Single Sample Scoring')
@data_option
@design_option
@output_option
@control_option
def z_score(data, design, out, control) -> None:
    click.echo(f"Starting Z-Score Based Single Sample Scoring with {data} & {design} files and saving it to {out}")

    data_df = pd.read_csv(data, sep='\t', index_col=0)
    design_df = pd.read_csv(design, sep='\t', index_col=0)

    output = do_z_score(data=data_df, design=design_df, control=control)
    output.to_csv(out, sep='\t')

    click.echo(f"Done With Z-Score calculation for {data}")


@sample_scoring.command(help='ssGSEA based Single Sample Scoring')
@data_option
@output_option
@click.option(
    '--gs',
    help="Path to the .gmt geneset file",
    type=click.Path(file_okay=True, dir_okay=False, exists=False),
    required=True
)
@click.option(
    '--out_dir',
    help="Path to the output directory",
    type=click.Path(file_okay=False, dir_okay=True, exists=False),
    required=False,
    default=None,
    show_default=True
)
def ssgsea(data, out, gs, out_dir) -> None:
    click.echo(f"Starting Z-Score Based Single Sample Scoring with {data} & {gs} files and saving it to {out}")

    data_df = pd.read_csv(data, sep='\t', index_col=0)

    single_sample_gsea = do_ssgsea(data_df, gs, out_dir)
    single_sample_gsea.res2d.to_csv(out, sep='\t')

    click.echo(f"Done With ssgsea for {data}")


@main.group()
def embedding():
    """List Vectorization methods available."""


@embedding.command()
def row2vec():
    """Perform row based embedding"""
    click.echo(f"Starting Row2Vec")
    do_row2vec()
    click.echo(f"Done With Row2Vec")


@embedding.command()
def path2vec():
    """Perform pathway based embedding"""
    click.echo(f"Starting Path2Vec")
    do_path2vec()
    click.echo(f"Done With Path2Vec")


@embedding.command()
@data_option
@output_option
def thresh2vec(data, out) -> None:
    """Perform Threshold based Vectorization"""
    click.echo(f"Starting Thresh2Vec with {data}, and out-putting to {out}")

    data_df = pd.read_csv(data, sep='\t', index_col=0)

    output = do_thresh2vec(data=data_df)

    output.to_csv(out, sep='\t')

    click.echo(f"Done With Thresh2Vec for {data}")


@embedding.command()
@data_option
@design_option
@click.option(
    '--edge_out',
    help="Path to the output the edge-list file",
    type=click.Path(file_okay=True, dir_okay=False, exists=False),
    required=True
)
@click.option(
    '--edge_out_num',
    help="Path to the output the edge-list number file",
    type=click.Path(file_okay=True, dir_okay=False, exists=False),
    required=True
)
@click.option(
    '--label_edge',
    help="Path to the output the edge-list number file",
    type=click.Path(file_okay=True, dir_okay=False, exists=False),
    required=True
)
def nrl(data, design, edge_out, edge_out_num, label_edge):
    """Perform Network representation learning"""
    click.echo(f"Starting NRL")

    data_df = pd.read_csv(data, sep='\t')
    data_df.rename(columns={'Unnamed: 0': 'patients'}, inplace=True)

    design_df = pd.read_csv(design, sep='\t')

    with open(edge_out, 'w') as out, open(edge_out_num, 'w') as out_num, open(label_edge, 'w') as label_out:
        do_nrl(data_df, design_df, out, out_num, label_out)

    click.echo(f"Done With NRL")


if __name__ == '__main__':
    main()